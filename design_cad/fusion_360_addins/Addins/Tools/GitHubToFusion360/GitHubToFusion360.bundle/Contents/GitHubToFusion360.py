# Author-Jerome Briot
# Contact-jbtechlab@gmail.com
# Description-Install scripts or add-ins from GitHub

import adsk.core, traceback # pylint: disable=import-error
import os
import platform
import urllib
import urllib.request
import zipfile
import shutil
import tempfile

import xml.etree.ElementTree as etree

this_addin_name = 'GitHubToFusion360'
this_addin_version = '2.5.0'
this_addin_author = 'Jerome Briot'
this_addin_contact = 'jbtechlab@gmail.com'

this_addin_name += ' - v' + this_addin_version

debug_mode = False

def run(context):

    ui = None

    try:

        app = adsk.core.Application.get()
        ui = app.userInterface

        if not debug_mode:
            # Ask the user to enter the URL of the git repo to import in Fusion 360
            (github_url, cancelled) = ui.inputBox('Enter the URL of the GitHub repo to import in Fusion 360', this_addin_name)
            if cancelled:
                ui.messageBox('Process aborted', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                return
        else:
            # For debugging purpose only.
            # github_url = 'https://github.com/JeromeBriot/'

            # github_url = 'https://github.com/kantoku-code/Fusion360_Two-turn_Mobius_strip'
            # github_url = 'https://github.com/JeromeBriot/fusion360-check-computer-specifications'
            # github_url = 'https://github.com/JeromeBriot/fusion360-memory-used'
            # github_url = 'https://github.com/radzimir/fusion_worm_gear'
            # github_url = 'https://github.com/syuntoku14/fusion2urdf'
            # github_url = 'https://github.com/hanskellner/Fusion360Image2Surface'
            # github_url = 'https://github.com/tapnair/NESTER'
            # github_url = 'https://github.com/scottkildall/Fusion360FJBox'
            # github_url = 'https://github.com/opendesk/fusion360-dxf-export'
            # github_url = 'https://github.com/BradAndersonJr/GuitarEngine'
            # github_url = 'https://github.com/Virtual-FTC/Fusion_UnityExporterAddOn'

            # No manisfest file
            # github_url = 'https://github.com/pawelzwronek/fusion360-NoGestures'

            pass

        # Check the URL
        if not github_url.startswith('https://github.com/'):
            ui.messageBox('The URL must start with "https://github.com/"\n\nProcess aborted.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
            return

        # Remove trailing path separator
        if github_url.endswith('/'):
            github_url = github_url[:-1]

        # Get autodesk products path for Windows and Mac systems
        if platform.system() == 'Windows':
            autodesk_path = '/'.join([os.environ.get('APPDATA').replace('\\', '/'), 'Autodesk'])
        else:
            autodesk_path = '/'.join([os.environ.get('HOME'), 'Library', 'Application Support', 'Autodesk'])

        # Set the local path for scripts and add-ins.
        # This path should be the same as the one in the "General > API" menu
        # of the Preferences panel in Fusion 360 or in the options file
        # NMachineSpecificOptions.xml (if the file exists)

        path_set_correctly = False

        # Try to find the path in NMachineSpecificOptions.xml
        options_file = '/'.join([autodesk_path, 'Neutron Platform', 'Options', 'NMachineSpecificOptions.xml'])
        if os.path.isfile(options_file):
            # Ugly try-except block because of non valid XML file
            # https://forums.autodesk.com/t5/fusion-360-support/bug-nmachinespecificoptions-xml-not-valid-prefix-ironpostprocess/m-p/9332909
            try:
                tree = etree.parse(options_file)
                node = tree.find('./UIAPIMachineSpecificOptionGroup/DefaultAPIPath')
                if node is not None and 'Value' in node.attrib:
                    if os.path.isdir(node.attrib['Value']):
                        path_set_correctly = True
                        scripts_addins_path = node.attrib['Value']
            except:
                pass

        # If previous method failed, try to set api path using default location
        if not path_set_correctly:
            scripts_addins_path = '/'.join([autodesk_path, 'Autodesk Fusion 360', 'API'])
            if os.path.isdir(scripts_addins_path):
                path_set_correctly = True

        # If previous methods failed, then ask the user for the local path for scripts and add-in
        if not path_set_correctly:
            (scripts_addins_path, cancelled) = ui.inputBox('Enter path to the folder where scripts and add-ins are installed', this_addin_name)
            if cancelled:
                ui.messageBox('Process aborted.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                return
            else:
                if not os.path.isdir(scripts_addins_path):
                    ui.messageBox('"{}" is not a valid path\n\nProcess aborted.'.format(scripts_addins_path))
                    return

        # Get the name of the repo and the name of its owner
        owner, repo = github_url.split('/')[3:5]

        # URL to the main zip file
        zipball_url = '/'.join(['https://api.github.com/repos', owner, repo, 'zipball'])

        # URL request
        request = urllib.request.Request(zipball_url, headers={"Accept": "application/vnd.github.v3+json"})

        # Check if the URL is reachable
        try:
            result = urllib.request.urlopen(request)
            zipball_found = True
        except urllib.error.HTTPError as e:
            msg = '{}\n\n  The server couldn\'t fulfill the request.\n  {}\n\n'.format(zipball_url, e)
            zipball_found = False
        except urllib.error.URLError as e:
            msg = '{}\n\n  Fail to reach a server.\n  {}\n\n'.format(zipball_url, e.reason)
            zipball_found = False

        if not zipball_found:
            ui.messageBox(msg, this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
            return

        # Create a local temporary folder
        with tempfile.TemporaryDirectory(prefix='GitHubToFusion360_') as tempdir:

            # Download the main zip file in the temporary folder
            local_zip = '/'.join([tempdir, 'zipball.zip'])

            try:
                zippedData = result.read()
                output = open(local_zip, 'wb')
                output.write(zippedData)
                output.close()
            except:
                if ui:
                    ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                    return
            try:
                zf = zipfile.ZipFile(local_zip, 'r')
            except zipfile.BadZipfile as e:
                ui.messageBox('No valid zip file found in the repo.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                return

            # Search for the manifest file in the zip file
            # Name of the file is the name of the add-in
            manifest_found = False

            root_dir_in_zip_file = zf.namelist()[0]

            for name in zf.namelist():
                fileparts = name.split('/')
                if fileparts[-1].endswith('.manifest') and fileparts[-1] != 'Fusion360AddinSkeleton.manifest':
                    addin_name = fileparts[-1][:-9]
                    manifest_found = True
                    manifest_file = name.replace(root_dir_in_zip_file, '')
                    break

            if not manifest_found:
                ui.messageBox('No manifest file found in the zip file\n\nProcess aborted.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                zf.close()
                os.remove(local_zip)
                return

            # Unzip the local master zip file in the temporary folder
            zf.extractall(path=tempdir)

            zf.close()

            # Delete the local master zip file
            os.remove(local_zip)

            # Rename the add-in folder according to the manifest file name
            os.rename('/'.join([tempdir, root_dir_in_zip_file]), '/'.join([tempdir, addin_name]))

            # Extract informations from the manifest file
            with open(r'/'.join([tempdir, addin_name, manifest_file]), 'r') as f:
                for line in f:
                    words = line.split()
                    if words[0].find('autodeskProduct') > 0 and words[1].find('Fusion360') == -1:
                        ui.messageBox('Wrong product found in the manifest file: {}\n\nProcess aborted.'.format(words[1]), this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                    elif words[0].find('type') > 0:
                        if words[1].find('addin') > 0:
                            contrib_type = 'add-in'
                            dest_path = '/'.join([scripts_addins_path, 'Addins'])
                        elif words[1].find('script') > 0:
                            contrib_type = 'script'
                            dest_path = '/'.join([scripts_addins_path, 'Scripts'])
                        else:
                            ui.messageBox('Unable to determine if the zip file contains a script or an add-in.\n\nProcess aborted.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                    elif words[0].find('supportedOS') > 0:
                        if (platform.system() == 'Windows' and words[1].find('windows') == -1) or (platform.system() == 'Darwin' and words[1].find('mac') == -1):
                            ui.messageBox('Your OS is not marked as available for this add-in.\n\nInstallation process will continue anyway.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.WarningIconType)

            # Ask confirmation before moving the folder to its final destination
            result = ui.messageBox('Install the "{}" {} from the GitHub repo:\n\n   {}\n\nIn the folder below?\n\n   {}'.format(addin_name, contrib_type, github_url, dest_path), this_addin_name, adsk.core.MessageBoxButtonTypes.YesNoButtonType, adsk.core.MessageBoxIconTypes.QuestionIconType)

            if result == adsk.core.DialogResults.DialogYes:  # YES

                # Check if the add-in is already installed
                if os.path.isdir('/'.join([dest_path, addin_name])):
                    result = ui.messageBox('The "{}" {} seems to be already installed.\n\nDelete previous install?'.format(addin_name, contrib_type), this_addin_name, adsk.core.MessageBoxButtonTypes.YesNoButtonType, adsk.core.MessageBoxIconTypes.QuestionIconType)
                    if result == adsk.core.DialogResults.DialogYes:  # YES
                        shutil.rmtree('/'.join([dest_path, addin_name]))
                    else:  # NO
                        ui.messageBox('Process aborted', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)
                        return

                # Check if the manifest file is in a subfolder
                manifest_file_path = manifest_file.split('/')[:-1]
                # Move add-in files from the temporary folder to the destination folder
                shutil.move('/'.join([tempdir, addin_name] + manifest_file_path), dest_path)

                ui.messageBox('{} {} installation succeed.'.format(addin_name, contrib_type), this_addin_name)

            else:  # NO
                ui.messageBox('Process aborted.', this_addin_name, adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
