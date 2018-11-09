// Customizable Card Box v1.3
// by Lufton (https://www.facebook.com/dubovikmax)
// https://www.thingiverse.com/thing:2404395
//
// Thanks to:
// Thingiverse user "Benjamin" for his "Stencil-o-Matic" https://www.thingiverse.com/thing:55821
// Thingiverse user "TheNewHobbyist" for his "Card Case Customizer" https://www.thingiverse.com/thing:66327
//
// Change Log:
//
// 07/01/2017 - v1.3
// - Fixed gap calculation, now gap decreasing both lid and box top thickness proportionally
//
// 06/29/2017 - v1.2
// - Fixed spacers location calculation
//
// 06/28/2017 - v1.1
// - Now you can divide your box with spacers
// - Improve Customizer GUI 
//
// 06/26/2017 - v1.0
// - Initial Release
//

/* [General] */

// Choose what part you want to build
part = "both"; // [both:Both, box:Box, lid:Lid]
// Deck width. Don't forget to leave some extra space.
deck_width = 65; // [5:.1:500]
// Deck length. Don't forget to leave some extra space.
deck_length = 95; // [5:.1:500]
// Coma separated deck thicknesses
deck_thicknesses = [25];
// Spacer between decks
deck_spacer = .9; // [.1:.1:5]
// Box lid height
lid_height = 20; // [5:.1:100]
// Wall thickness. Choose carefully so your printer can make at least 2 outlines at the narrowest part (top of the box and lid). For 0.4 nozzle this should be at least 1.6.
wall_thickness = 1.8; // [0.2:.1:10]
// Space between lid and box top. The smaller this parameter will be, the tighter box will close.
gap = .1; // [.0:0.02:1.0]
// Depth of text and logo engrave. Depth < 0 will make relief.
engrave_depth = -.9; // [-10:.1:10]
enable_engrave = false;
// Whether to engrave both sides of the box
mirror = true;

/* [Text line 1] */

// First text line to engrave
text_1 = "Exploding";
// First text line font size
text_1_size = 10; //[.1:.1:50]
// First text line font family. You can use one of available fonts or select ***CUSTOM***.
text_1_font = "Roboto"; // [***CUSTOM***, ABeeZee,Abel,Abril Fatface,Aclonica,Acme,Actor,Adamina,Advent Pro,Aguafina Script,Akronim,Aladin,Aldrich,Alef,Alegreya,Alegreya SC,Alegreya Sans,Alegreya Sans SC,Alex Brush,Alfa Slab One,Alice,Alike,Alike Angular,Allan,Allerta,Allerta Stencil,Allura,Almendra,Almendra Display,Almendra SC,Amarante,Amaranth,Amatic SC,Amethysta,Amiri,Amita,Anaheim,Andada,Andika,Angkor,Annie Use Your Telescope,Anonymous Pro,Antic,Antic Didone,Antic Slab,Anton,Arapey,Arbutus,Arbutus Slab,Architects Daughter,Archivo Black,Archivo Narrow,Arimo,Arizonia,Armata,Artifika,Arvo,Arya,Asap,Asar,Asset,Astloch,Asul,Atomic Age,Aubrey,Audiowide,Autour One,Average,Average Sans,Averia Gruesa Libre,Averia Libre,Averia Sans Libre,Averia Serif Libre,Bad Script,Balthazar,Bangers,Basic,Battambang,Baumans,Bayon,Belgrano,Belleza,BenchNine,Bentham,Berkshire Swash,Bevan,Bigelow Rules,Bigshot One,Bilbo,Bilbo Swash Caps,Biryani,Bitter,Black Ops One,Bokor,Bonbon,Boogaloo,Bowlby One,Bowlby One SC,Brawler,Bree Serif,Bubblegum Sans,Bubbler One,Buda,Buenard,Butcherman,Butterfly Kids,Cabin,Cabin Condensed,Cabin Sketch,Caesar Dressing,Cagliostro,Calligraffitti,Cambay,Cambo,Candal,Cantarell,Cantata One,Cantora One,Capriola,Cardo,Carme,Carrois Gothic,Carrois Gothic SC,Carter One,Catamaran,Caudex,Caveat,Caveat Brush,Cedarville Cursive,Ceviche One,Changa One,Chango,Chau Philomene One,Chela One,Chelsea Market,Chenla,Cherry Cream Soda,Cherry Swash,Chewy,Chicle,Chivo,Chonburi,Cinzel,Cinzel Decorative,Clicker Script,Coda,Coda Caption,Codystar,Combo,Comfortaa,Coming Soon,Concert One,Condiment,Content,Contrail One,Convergence,Cookie,Copse,Corben,Courgette,Cousine,Coustard,Covered By Your Grace,Crafty Girls,Creepster,Crete Round,Crimson Text,Croissant One,Crushed,Cuprum,Cutive,Cutive Mono,Damion,Dancing Script,Dangrek,Dawning of a New Day,Days One,Dekko,Delius,Delius Swash Caps,Delius Unicase,Della Respira,Denk One,Devonshire,Dhurjati,Didact Gothic,Diplomata,Diplomata SC,Domine,Donegal One,Doppio One,Dorsa,Dosis,Dr Sugiyama,Droid Sans,Droid Sans Mono,Droid Serif,Duru Sans,Dynalight,EB Garamond,Eagle Lake,Eater,Economica,Eczar,Ek Mukta,Electrolize,Elsie,Elsie Swash Caps,Emblema One,Emilys Candy,Engagement,Englebert,Enriqueta,Erica One,Esteban,Euphoria Script,Ewert,Exo,Exo 2,Expletus Sans,Fanwood Text,Fascinate,Fascinate Inline,Faster One,Fasthand,Fauna One,Federant,Federo,Felipa,Fenix,Finger Paint,Fira Mono,Fira Sans,Fjalla One,Fjord One,Flamenco,Flavors,Fondamento,Fontdiner Swanky,Forum,Francois One,Freckle Face,Fredericka the Great,Fredoka One,Freehand,Fresca,Frijole,Fruktur,Fugaz One,GFS Didot,GFS Neohellenic,Gabriela,Gafata,Galdeano,Galindo,Gentium Basic,Gentium Book Basic,Geo,Geostar,Geostar Fill,Germania One,Gidugu,Gilda Display,Give You Glory,Glass Antiqua,Glegoo,Gloria Hallelujah,Goblin One,Gochi Hand,Gorditas,Goudy Bookletter 1911,Graduate,Grand Hotel,Gravitas One,Great Vibes,Griffy,Gruppo,Gudea,Gurajada,Habibi,Halant,Hammersmith One,Hanalei,Hanalei Fill,Handlee,Hanuman,Happy Monkey,Headland One,Henny Penny,Herr Von Muellerhoff,Hind,Hind Siliguri,Hind Vadodara,Holtwood One SC,Homemade Apple,Homenaje,IM Fell DW Pica,IM Fell DW Pica SC,IM Fell Double Pica,IM Fell Double Pica SC,IM Fell English,IM Fell English SC,IM Fell French Canon,IM Fell French Canon SC,IM Fell Great Primer,IM Fell Great Primer SC,Iceberg,Iceland,Imprima,Inconsolata,Inder,Indie Flower,Inika,Inknut Antiqua,Irish Grover,Istok Web,Italiana,Italianno,Itim,Jacques Francois,Jacques Francois Shadow,Jaldi,Jim Nightshade,Jockey One,Jolly Lodger,Josefin Sans,Josefin Slab,Joti One,Judson,Julee,Julius Sans One,Junge,Jura,Just Another Hand,Just Me Again Down Here,Kadwa,Kalam,Kameron,Kantumruy,Karla,Karma,Kaushan Script,Kavoon,Kdam Thmor,Keania One,Kelly Slab,Kenia,Khand,Khmer,Khula,Kite One,Knewave,Kotta One,Koulen,Kranky,Kreon,Kristi,Krona One,Kurale,La Belle Aurore,Laila,Lakki Reddy,Lancelot,Lateef,Lato,League Script,Leckerli One,Ledger,Lekton,Lemon,Libre Baskerville,Life Savers,Lilita One,Lily Script One,Limelight,Linden Hill,Lobster,Lobster Two,Londrina Outline,Londrina Shadow,Londrina Sketch,Londrina Solid,Lora,Love Ya Like A Sister,Loved by the King,Lovers Quarrel,Luckiest Guy,Lusitana,Lustria,Macondo,Macondo Swash Caps,Magra,Maiden Orange,Mako,Mallanna,Mandali,Marcellus,Marcellus SC,Marck Script,Margarine,Marko One,Marmelad,Martel,Martel Sans,Marvel,Mate,Mate SC,Maven Pro,McLaren,Meddon,MedievalSharp,Medula One,Megrim,Meie Script,Merienda,Merienda One,Merriweather,Merriweather Sans,Metal,Metal Mania,Metamorphous,Metrophobic,Michroma,Milonga,Miltonian,Miltonian Tattoo,Miniver,Miss Fajardose,Modak,Modern Antiqua,Molengo,Molle,Monda,Monofett,Monoton,Monsieur La Doulaise,Montaga,Montez,Montserrat,Montserrat Alternates,Montserrat Subrayada,Moul,Moulpali,Mountains of Christmas,Mouse Memoirs,Mr Bedfort,Mr Dafoe,Mr De Haviland,Mrs Saint Delafield,Mrs Sheppards,Muli,Mystery Quest,NTR,Neucha,Neuton,New Rocker,News Cycle,Niconne,Nixie One,Nobile,Nokora,Norican,Nosifer,Nothing You Could Do,Noticia Text,Noto Sans,Noto Serif,Nova Cut,Nova Flat,Nova Mono,Nova Oval,Nova Round,Nova Script,Nova Slim,Nova Square,Numans,Nunito,Odor Mean Chey,Offside,Old Standard TT,Oldenburg,Oleo Script,Oleo Script Swash Caps,Open Sans,Open Sans Condensed,Oranienbaum,Orbitron,Oregano,Orienta,Original Surfer,Oswald,Over the Rainbow,Overlock,Overlock SC,Ovo,Oxygen,Oxygen Mono,PT Mono,PT Sans,PT Sans Caption,PT Sans Narrow,PT Serif,PT Serif Caption,Pacifico,Palanquin,Palanquin Dark,Paprika,Parisienne,Passero One,Passion One,Pathway Gothic One,Patrick Hand,Patrick Hand SC,Patua One,Paytone One,Peddana,Peralta,Permanent Marker,Petit Formal Script,Petrona,Philosopher,Piedra,Pinyon Script,Pirata One,Plaster,Play,Playball,Playfair Display,Playfair Display SC,Podkova,Poiret One,Poller One,Poly,Pompiere,Pontano Sans,Poppins,Port Lligat Sans,Port Lligat Slab,Pragati Narrow,Prata,Preahvihear,Press Start 2P,Princess Sofia,Prociono,Prosto One,Puritan,Purple Purse,Quando,Quantico,Quattrocento,Quattrocento Sans,Questrial,Quicksand,Quintessential,Qwigley,Racing Sans One,Radley,Rajdhani,Raleway,Raleway Dots,Ramabhadra,Ramaraja,Rambla,Rammetto One,Ranchers,Rancho,Ranga,Rationale,Ravi Prakash,Redressed,Reenie Beanie,Revalia,Rhodium Libre,Ribeye,Ribeye Marrow,Righteous,Risque,Roboto,Roboto Condensed,Roboto Mono,Roboto Slab,Rochester,Rock Salt,Rokkitt,Romanesco,Ropa Sans,Rosario,Rosarivo,Rouge Script,Rozha One,Rubik,Rubik Mono One,Rubik One,Ruda,Rufina,Ruge Boogie,Ruluko,Rum Raisin,Ruslan Display,Russo One,Ruthie,Rye,Sacramento,Sahitya,Sail,Salsa,Sanchez,Sancreek,Sansita One,Sarala,Sarina,Sarpanch,Satisfy,Scada,Scheherazade,Schoolbell,Seaweed Script,Sevillana,Seymour One,Shadows Into Light,Shadows Into Light Two,Shanti,Share,Share Tech,Share Tech Mono,Shojumaru,Short Stack,Siemreap,Sigmar One,Signika,Signika Negative,Simonetta,Sintony,Sirin Stencil,Six Caps,Skranji,Slabo 13px,Slabo 27px,Slackey,Smokum,Smythe,Sniglet,Snippet,Snowburst One,Sofadi One,Sofia,Sonsie One,Sorts Mill Goudy,Source Code Pro,Source Sans Pro,Source Serif Pro,Special Elite,Spicy Rice,Spinnaker,Spirax,Squada One,Sree Krushnadevaraya,Stalemate,Stalinist One,Stardos Stencil,Stint Ultra Condensed,Stint Ultra Expanded,Stoke,Strait,Sue Ellen Francisco,Sumana,Sunshiney,Supermercado One,Sura,Suranna,Suravaram,Suwannaphum,Swanky and Moo Moo,Syncopate,Tangerine,Taprom,Tauri,Teko,Telex,Tenali Ramakrishna,Tenor Sans,Text Me One,The Girl Next Door,Tienne,Tillana,Timmana,Tinos,Titan One,Titillium Web,Trade Winds,Trocchi,Trochut,Trykker,Tulpen One,Ubuntu,Ubuntu Condensed,Ubuntu Mono,Ultra,Uncial Antiqua,Underdog,Unica One,UnifrakturCook,UnifrakturMaguntia,Unkempt,Unlock,Unna,VT323,Vampiro One,Varela,Varela Round,Vast Shadow,Vesper Libre,Vibur,Vidaloka,Viga,Voces,Volkhov,Vollkorn,Voltaire,Waiting for the Sunrise,Wallpoet,Walter Turncoat,Warnes,Wellfleet,Wendy One,Wire One,Work Sans,Yanone Kaffeesatz,Yantramanav,Yellowtail,Yeseva One,Yesteryear,Zeyada]
// First text line font style
text_1_font_style = "Regular"; // [Regular, Bold, Italic, Bold Italic]
// Custom google font family name. You can also include style, e.g. "Roboto:style=Bold Italic"
text_1_custom_font = "Roboto";
// First text line alignment
text_1_align = "ct"; // [lt:Left-Top, ct:Center-Top, rt:Right-Top, lc:Left-Middle, cc:Center, rc:Right-Middle, lb:Left-Bottom, cb:Center-Bottom, rb:Right-Bottom]
// First text line horizontal offset (> 0 - right, < 0 - left)
text_1_x_offset = 0; // [-100:0.1:100]
// First text line vertical offset (> 0 - upper, < 0 - lower)
text_1_y_offset = -5; // [-100:0.1:100]

/* [Text line 2] */

// Second text line to engrave
text_2 = "Kittens";
// Second text line font size
text_2_size = 10; //[.1:.1:50]
// Second text line font family. You can use one of available fonts or select ***CUSTOM***.
text_2_font = "Roboto"; // [***CUSTOM***, ABeeZee,Abel,Abril Fatface,Aclonica,Acme,Actor,Adamina,Advent Pro,Aguafina Script,Akronim,Aladin,Aldrich,Alef,Alegreya,Alegreya SC,Alegreya Sans,Alegreya Sans SC,Alex Brush,Alfa Slab One,Alice,Alike,Alike Angular,Allan,Allerta,Allerta Stencil,Allura,Almendra,Almendra Display,Almendra SC,Amarante,Amaranth,Amatic SC,Amethysta,Amiri,Amita,Anaheim,Andada,Andika,Angkor,Annie Use Your Telescope,Anonymous Pro,Antic,Antic Didone,Antic Slab,Anton,Arapey,Arbutus,Arbutus Slab,Architects Daughter,Archivo Black,Archivo Narrow,Arimo,Arizonia,Armata,Artifika,Arvo,Arya,Asap,Asar,Asset,Astloch,Asul,Atomic Age,Aubrey,Audiowide,Autour One,Average,Average Sans,Averia Gruesa Libre,Averia Libre,Averia Sans Libre,Averia Serif Libre,Bad Script,Balthazar,Bangers,Basic,Battambang,Baumans,Bayon,Belgrano,Belleza,BenchNine,Bentham,Berkshire Swash,Bevan,Bigelow Rules,Bigshot One,Bilbo,Bilbo Swash Caps,Biryani,Bitter,Black Ops One,Bokor,Bonbon,Boogaloo,Bowlby One,Bowlby One SC,Brawler,Bree Serif,Bubblegum Sans,Bubbler One,Buda,Buenard,Butcherman,Butterfly Kids,Cabin,Cabin Condensed,Cabin Sketch,Caesar Dressing,Cagliostro,Calligraffitti,Cambay,Cambo,Candal,Cantarell,Cantata One,Cantora One,Capriola,Cardo,Carme,Carrois Gothic,Carrois Gothic SC,Carter One,Catamaran,Caudex,Caveat,Caveat Brush,Cedarville Cursive,Ceviche One,Changa One,Chango,Chau Philomene One,Chela One,Chelsea Market,Chenla,Cherry Cream Soda,Cherry Swash,Chewy,Chicle,Chivo,Chonburi,Cinzel,Cinzel Decorative,Clicker Script,Coda,Coda Caption,Codystar,Combo,Comfortaa,Coming Soon,Concert One,Condiment,Content,Contrail One,Convergence,Cookie,Copse,Corben,Courgette,Cousine,Coustard,Covered By Your Grace,Crafty Girls,Creepster,Crete Round,Crimson Text,Croissant One,Crushed,Cuprum,Cutive,Cutive Mono,Damion,Dancing Script,Dangrek,Dawning of a New Day,Days One,Dekko,Delius,Delius Swash Caps,Delius Unicase,Della Respira,Denk One,Devonshire,Dhurjati,Didact Gothic,Diplomata,Diplomata SC,Domine,Donegal One,Doppio One,Dorsa,Dosis,Dr Sugiyama,Droid Sans,Droid Sans Mono,Droid Serif,Duru Sans,Dynalight,EB Garamond,Eagle Lake,Eater,Economica,Eczar,Ek Mukta,Electrolize,Elsie,Elsie Swash Caps,Emblema One,Emilys Candy,Engagement,Englebert,Enriqueta,Erica One,Esteban,Euphoria Script,Ewert,Exo,Exo 2,Expletus Sans,Fanwood Text,Fascinate,Fascinate Inline,Faster One,Fasthand,Fauna One,Federant,Federo,Felipa,Fenix,Finger Paint,Fira Mono,Fira Sans,Fjalla One,Fjord One,Flamenco,Flavors,Fondamento,Fontdiner Swanky,Forum,Francois One,Freckle Face,Fredericka the Great,Fredoka One,Freehand,Fresca,Frijole,Fruktur,Fugaz One,GFS Didot,GFS Neohellenic,Gabriela,Gafata,Galdeano,Galindo,Gentium Basic,Gentium Book Basic,Geo,Geostar,Geostar Fill,Germania One,Gidugu,Gilda Display,Give You Glory,Glass Antiqua,Glegoo,Gloria Hallelujah,Goblin One,Gochi Hand,Gorditas,Goudy Bookletter 1911,Graduate,Grand Hotel,Gravitas One,Great Vibes,Griffy,Gruppo,Gudea,Gurajada,Habibi,Halant,Hammersmith One,Hanalei,Hanalei Fill,Handlee,Hanuman,Happy Monkey,Headland One,Henny Penny,Herr Von Muellerhoff,Hind,Hind Siliguri,Hind Vadodara,Holtwood One SC,Homemade Apple,Homenaje,IM Fell DW Pica,IM Fell DW Pica SC,IM Fell Double Pica,IM Fell Double Pica SC,IM Fell English,IM Fell English SC,IM Fell French Canon,IM Fell French Canon SC,IM Fell Great Primer,IM Fell Great Primer SC,Iceberg,Iceland,Imprima,Inconsolata,Inder,Indie Flower,Inika,Inknut Antiqua,Irish Grover,Istok Web,Italiana,Italianno,Itim,Jacques Francois,Jacques Francois Shadow,Jaldi,Jim Nightshade,Jockey One,Jolly Lodger,Josefin Sans,Josefin Slab,Joti One,Judson,Julee,Julius Sans One,Junge,Jura,Just Another Hand,Just Me Again Down Here,Kadwa,Kalam,Kameron,Kantumruy,Karla,Karma,Kaushan Script,Kavoon,Kdam Thmor,Keania One,Kelly Slab,Kenia,Khand,Khmer,Khula,Kite One,Knewave,Kotta One,Koulen,Kranky,Kreon,Kristi,Krona One,Kurale,La Belle Aurore,Laila,Lakki Reddy,Lancelot,Lateef,Lato,League Script,Leckerli One,Ledger,Lekton,Lemon,Libre Baskerville,Life Savers,Lilita One,Lily Script One,Limelight,Linden Hill,Lobster,Lobster Two,Londrina Outline,Londrina Shadow,Londrina Sketch,Londrina Solid,Lora,Love Ya Like A Sister,Loved by the King,Lovers Quarrel,Luckiest Guy,Lusitana,Lustria,Macondo,Macondo Swash Caps,Magra,Maiden Orange,Mako,Mallanna,Mandali,Marcellus,Marcellus SC,Marck Script,Margarine,Marko One,Marmelad,Martel,Martel Sans,Marvel,Mate,Mate SC,Maven Pro,McLaren,Meddon,MedievalSharp,Medula One,Megrim,Meie Script,Merienda,Merienda One,Merriweather,Merriweather Sans,Metal,Metal Mania,Metamorphous,Metrophobic,Michroma,Milonga,Miltonian,Miltonian Tattoo,Miniver,Miss Fajardose,Modak,Modern Antiqua,Molengo,Molle,Monda,Monofett,Monoton,Monsieur La Doulaise,Montaga,Montez,Montserrat,Montserrat Alternates,Montserrat Subrayada,Moul,Moulpali,Mountains of Christmas,Mouse Memoirs,Mr Bedfort,Mr Dafoe,Mr De Haviland,Mrs Saint Delafield,Mrs Sheppards,Muli,Mystery Quest,NTR,Neucha,Neuton,New Rocker,News Cycle,Niconne,Nixie One,Nobile,Nokora,Norican,Nosifer,Nothing You Could Do,Noticia Text,Noto Sans,Noto Serif,Nova Cut,Nova Flat,Nova Mono,Nova Oval,Nova Round,Nova Script,Nova Slim,Nova Square,Numans,Nunito,Odor Mean Chey,Offside,Old Standard TT,Oldenburg,Oleo Script,Oleo Script Swash Caps,Open Sans,Open Sans Condensed,Oranienbaum,Orbitron,Oregano,Orienta,Original Surfer,Oswald,Over the Rainbow,Overlock,Overlock SC,Ovo,Oxygen,Oxygen Mono,PT Mono,PT Sans,PT Sans Caption,PT Sans Narrow,PT Serif,PT Serif Caption,Pacifico,Palanquin,Palanquin Dark,Paprika,Parisienne,Passero One,Passion One,Pathway Gothic One,Patrick Hand,Patrick Hand SC,Patua One,Paytone One,Peddana,Peralta,Permanent Marker,Petit Formal Script,Petrona,Philosopher,Piedra,Pinyon Script,Pirata One,Plaster,Play,Playball,Playfair Display,Playfair Display SC,Podkova,Poiret One,Poller One,Poly,Pompiere,Pontano Sans,Poppins,Port Lligat Sans,Port Lligat Slab,Pragati Narrow,Prata,Preahvihear,Press Start 2P,Princess Sofia,Prociono,Prosto One,Puritan,Purple Purse,Quando,Quantico,Quattrocento,Quattrocento Sans,Questrial,Quicksand,Quintessential,Qwigley,Racing Sans One,Radley,Rajdhani,Raleway,Raleway Dots,Ramabhadra,Ramaraja,Rambla,Rammetto One,Ranchers,Rancho,Ranga,Rationale,Ravi Prakash,Redressed,Reenie Beanie,Revalia,Rhodium Libre,Ribeye,Ribeye Marrow,Righteous,Risque,Roboto,Roboto Condensed,Roboto Mono,Roboto Slab,Rochester,Rock Salt,Rokkitt,Romanesco,Ropa Sans,Rosario,Rosarivo,Rouge Script,Rozha One,Rubik,Rubik Mono One,Rubik One,Ruda,Rufina,Ruge Boogie,Ruluko,Rum Raisin,Ruslan Display,Russo One,Ruthie,Rye,Sacramento,Sahitya,Sail,Salsa,Sanchez,Sancreek,Sansita One,Sarala,Sarina,Sarpanch,Satisfy,Scada,Scheherazade,Schoolbell,Seaweed Script,Sevillana,Seymour One,Shadows Into Light,Shadows Into Light Two,Shanti,Share,Share Tech,Share Tech Mono,Shojumaru,Short Stack,Siemreap,Sigmar One,Signika,Signika Negative,Simonetta,Sintony,Sirin Stencil,Six Caps,Skranji,Slabo 13px,Slabo 27px,Slackey,Smokum,Smythe,Sniglet,Snippet,Snowburst One,Sofadi One,Sofia,Sonsie One,Sorts Mill Goudy,Source Code Pro,Source Sans Pro,Source Serif Pro,Special Elite,Spicy Rice,Spinnaker,Spirax,Squada One,Sree Krushnadevaraya,Stalemate,Stalinist One,Stardos Stencil,Stint Ultra Condensed,Stint Ultra Expanded,Stoke,Strait,Sue Ellen Francisco,Sumana,Sunshiney,Supermercado One,Sura,Suranna,Suravaram,Suwannaphum,Swanky and Moo Moo,Syncopate,Tangerine,Taprom,Tauri,Teko,Telex,Tenali Ramakrishna,Tenor Sans,Text Me One,The Girl Next Door,Tienne,Tillana,Timmana,Tinos,Titan One,Titillium Web,Trade Winds,Trocchi,Trochut,Trykker,Tulpen One,Ubuntu,Ubuntu Condensed,Ubuntu Mono,Ultra,Uncial Antiqua,Underdog,Unica One,UnifrakturCook,UnifrakturMaguntia,Unkempt,Unlock,Unna,VT323,Vampiro One,Varela,Varela Round,Vast Shadow,Vesper Libre,Vibur,Vidaloka,Viga,Voces,Volkhov,Vollkorn,Voltaire,Waiting for the Sunrise,Wallpoet,Walter Turncoat,Warnes,Wellfleet,Wendy One,Wire One,Work Sans,Yanone Kaffeesatz,Yantramanav,Yellowtail,Yeseva One,Yesteryear,Zeyada]
// Second text line font style
text_2_font_style = "Regular"; // [Regular, Bold, Italic, Bold Italic]
// Second text line custom google font family name. You can also include style, e.g. "Roboto:style=Bold Italic"
text_2_custom_font = "Roboto";
// Second text line alignment
text_2_align = "cb"; // [lt:Left-Top, ct:Center-Top, rt:Right-Top, lc:Left-Middle, cc:Center, rc:Right-Middle, lb:Left-Bottom, cb:Center-Bottom, rb:Right-Bottom]
// Second text line horizontal offset (> 0 - right, < 0 - left)
text_2_x_offset = 0; // [-100:0.1:100]
// Second text line vertical offset (> 0 - upper, < 0 - lower)
text_2_y_offset = 5; // [-100:0.1:100]

/* [Logo] */

//Logo data generated at www.chaaawa.com/stencil_factory_js/
logo_data = [[441, 384, 1],[1,[[354.57,2],[352.91,0.5],[352.96,2.75],[352.96,2.75],[353.29,4.847],[354.162,8.891],[357,20.5],[357,20.5],[358.694,27.473],[359.956,33.565],[361.03,42.25],[361.03,42.25],[360.959,45.299],[360.672,47.513],[359.28,50.22],[359.28,50.22],[358.286,50.913],[356.942,51.466],[353.75,51.97],[353.75,51.97],[351.525,51.83],[348.237,51.425],[340.25,50.07],[340.25,50.07],[335.834,49.266],[331.015,48.505],[322.5,47.45],[322.5,47.45],[317.988,47.22],[313.358,47.377],[301,49.06],[301,49.06],[293.833,50.217],[289.097,50.745],[283,50.15],[283,50.15],[280.653,49.234],[277.626,47.646],[271,43.29],[271,43.29],[267.498,40.648],[263.503,37.623],[256,31.92],[256,31.92],[252.3,29.013],[247.767,25.345],[238.5,17.6],[238.5,17.6],[234.242,14.074],[230.041,10.806],[223.75,6.51],[223.75,6.51],[221.906,5.574],[220.396,4.882],[219,4.5],[219,4.5],[219.168,5.031],[219.627,6.102],[221.14,9.25],[221.14,9.25],[222.291,11.374],[223.84,14.014],[227.32,19.5],[227.32,19.5],[229.366,22.457],[231.955,26.073],[237.43,33.45],[237.43,33.45],[240.004,36.855],[242.526,40.252],[246.25,45.45],[246.25,45.45],[247.318,47.26],[248.197,49.192],[249.02,52.5],[249.02,52.5],[248.518,54.744],[247.086,58.573],[242.04,69.5],[242.04,69.5],[238.819,76.254],[235.992,82.845],[231.76,94.96],[228.5,106.41],[225,108.71],[225,108.71],[223.178,109.681],[220.938,110.528],[216,111.59],[216,111.59],[212.486,112.087],[206.978,113.011],[193,115.61],[193,115.61],[185.181,117.214],[176.823,119.043],[162.5,122.47],[162.5,122.47],[156.624,124.08],[150.236,125.952],[139,129.539],[139,129.539],[134.097,131.35],[128.503,133.578],[118,138.15],[118,138.15],[113.018,140.675],[107.21,143.896],[96,150.76],[96,150.76],[90.418,154.698],[84.856,159.04],[74.38,168.46],[74.38,168.46],[69.919,173.113],[65.558,178.063],[58.71,187],[58.71,187],[56.355,190.737],[54.057,194.622],[50.68,201],[50.68,201],[49.597,203.611],[48.478,206.648],[46.66,212.5],[46.66,212.5],[45.997,215.46],[45.348,219.087],[44.39,226.5],[44.39,226.5],[44.019,229.962],[43.545,233.473],[42.52,239],[41.37,243.5],[32.439,249.68],[32.439,249.68],[28.455,252.583],[24.217,255.92],[17,262.25],[17,262.25],[14.182,265.236],[11.308,268.648],[6.75,275.07],[6.75,275.07],[5.096,278.237],[3.578,281.791],[1.36,289],[1.36,289],[0.667,292.753],[0.265,296.377],[0.31,303.5],[0.31,303.5],[0.739,306.849],[1.465,310.793],[3.4,318.5],[3.4,318.5],[4.798,322.372],[6.632,326.5],[11.11,334.5],[11.11,334.5],[13.662,338.119],[16.743,342.061],[22.94,349],[22.94,349],[26.206,352.004],[30.235,355.373],[38.52,361.56],[38.52,361.56],[42.619,364.208],[47.14,366.93],[55.25,371.31],[55.25,371.31],[58.829,372.934],[62.851,374.628],[70.25,377.43],[70.25,377.43],[73.737,378.515],[77.87,379.67],[86,381.64],[86,381.64],[90.821,382.462],[96.321,383.013],[111,383.42],[111,383.42],[119.292,383.335],[125.413,383.044],[134,381.62],[134,381.62],[136.916,380.737],[140.057,379.663],[145.5,377.49],[145.5,377.49],[147.737,376.264],[150.133,374.648],[154.25,371.08],[154.25,371.08],[155.706,369.359],[156.905,367.684],[158.03,365.25],[158.03,365.25],[157.858,364.398],[157.377,363.37],[155.78,361.31],[155.78,361.31],[154.576,360.325],[152.992,359.272],[149.5,357.46],[149.5,357.46],[147.119,356.707],[143.592,355.883],[135,354.42],[135,354.42],[129.82,353.882],[123.473,353.438],[110.5,353.02],[110.5,353.02],[104.432,352.933],[98.262,352.713],[88.5,352.01],[88.5,352.01],[84.92,351.498],[81.087,350.846],[74.5,349.45],[74.5,349.45],[71.579,348.603],[68.061,347.456],[61,344.87],[61,344.87],[57.465,343.329],[53.38,341.366],[45.58,337.18],[45.58,337.18],[41.983,334.848],[38.037,331.965],[31.02,326],[31.02,326],[28.108,322.963],[25.665,320.031],[22.59,315],[22.59,315],[21.775,312.529],[21.293,309.943],[21.22,303.5],[21.22,303.5],[21.583,299.915],[22.245,296.611],[24.68,290],[24.68,290],[26.239,286.967],[28.255,283.511],[32.61,277.03],[37.5,270.56],[38.72,278.53],[38.72,278.53],[39.363,282.175],[40.212,286.213],[42.08,293.5],[42.08,293.5],[43.144,296.691],[44.47,300.206],[47.22,306.5],[47.22,306.5],[48.677,309.224],[50.43,312.206],[53.94,317.5],[53.94,317.5],[55.937,319.883],[58.208,322.038],[63.58,325.67],[63.58,325.67],[66.511,327.029],[70.112,328.391],[77.5,330.49],[77.5,330.49],[82.272,331.258],[88.308,331.807],[105.5,332.33],[105.5,332.33],[114.653,332.332],[121.567,332.157],[129.25,331.25],[129.25,331.25],[130.824,330.586],[132.341,329.706],[134.51,327.75],[134.51,327.75],[135.096,326.678],[135.576,325.427],[136.02,323],[136.02,323],[135.787,321.656],[135.141,319.84],[133.01,315.75],[133.01,315.75],[131.843,313.866],[130.886,312.247],[130,310.5],[130,310.5],[130.197,310.307],[130.736,310.148],[132.5,310],[132.5,310],[134.044,310.271],[136.396,311.012],[142.25,313.45],[142.25,313.45],[146.395,315.169],[151.547,316.856],[165,320.18],[180.5,323.45],[204.5,323.51],[204.5,323.51],[213.995,323.553],[222.109,323.62],[230.75,323.79],[230.75,323.79],[231.833,324.023],[232.529,324.538],[233.02,326.75],[233.02,326.75],[233.164,327.981],[233.542,329.305],[234.77,331.59],[234.77,331.59],[235.677,332.566],[236.872,333.68],[239.5,335.77],[239.5,335.77],[241.138,336.759],[243.381,337.896],[248.5,340.06],[248.5,340.06],[251.777,341.079],[255.218,341.777],[263.67,342.37],[263.67,342.37],[268.52,342.361],[271.71,342.102],[275.67,340.41],[275.67,340.41],[276.88,339.368],[278.082,338.078],[279.91,335.41],[279.91,335.41],[280.543,333.808],[280.801,332.273],[280.23,328.5],[280.23,328.5],[279.826,326.937],[279.521,325.641],[279.33,324.38],[279.33,324.38],[279.908,324.398],[281.36,324.542],[286,325.11],[286,325.11],[290.577,325.442],[298.23,325.727],[318.5,326.03],[318.5,326.03],[329.03,325.983],[338.48,325.803],[350,325.15],[350,325.15],[352.157,324.813],[353.958,324.597],[355.75,324.6],[355.75,324.6],[355.528,325.051],[354.738,325.985],[351.95,328.75],[351.95,328.75],[350.185,330.546],[348.929,332.186],[347.95,335],[347.95,335],[348.103,336.165],[348.492,337.485],[349.74,339.94],[349.74,339.94],[350.701,340.996],[352.013,342.072],[355,343.77],[355,343.77],[357.645,344.425],[362.007,344.837],[378,345.05],[378,345.05],[386.481,344.936],[395.153,344.722],[409,344.11],[409,344.11],[414.37,343.638],[418.666,343.04],[424.41,341.4],[424.41,341.4],[426.096,340.467],[427.797,339.327],[430.45,337],[430.45,337],[431.45,335.519],[432.601,333.328],[434.79,328],[434.79,328],[435.775,324.649],[436.833,320.325],[438.66,311],[438.66,311],[439.398,305.184],[439.936,298.25],[440.41,281],[440.41,281],[440.347,272.345],[440.101,264.372],[439.14,252.5],[439.14,252.5],[438.421,248.058],[437.472,242.618],[435.37,231.5],[435.37,231.5],[434.047,225.341],[432.221,217.443],[428.03,200.5],[428.03,200.5],[425.59,191.307],[422.59,180.325],[416.43,158.5],[416.43,158.5],[413.651,148.859],[411.02,139.612],[407.38,126.5],[407.38,126.5],[406.259,121.625],[404.968,115.005],[402.52,100],[402.52,100],[401.403,92.616],[400.206,85.441],[398.14,75],[398.14,75],[397.165,71.616],[395.912,67.942],[393.22,61.5],[393.22,61.5],[391.582,58.579],[389.356,55.061],[384.3,48],[384.3,48],[381.765,44.735],[379.23,41.385],[375.33,36],[375.33,36],[373.842,33.663],[372.063,30.622],[368.52,24],[368.52,24],[366.728,20.577],[364.618,16.797],[360.5,10],[360.5,10],[358.71,7.356],[356.995,4.968],[354.57,2]]],[0,[[283,64.019],[283,64.019],[285.065,64.172],[287.355,64.576],[291.5,65.89],[291.5,65.89],[293.226,66.797],[294.969,67.896],[297.69,70.12],[297.69,70.12],[298.719,71.439],[299.896,73.27],[302.11,77.5],[302.11,77.5],[303.039,80.04],[303.837,83.061],[304.8,89.5],[304.8,89.5],[304.901,92.636],[304.797,95.667],[304.03,100.5],[304.03,100.5],[303.336,102.354],[302.373,104.447],[300.14,108.32],[300.14,108.32],[298.8,109.953],[297.101,111.579],[293.5,114.06],[293.5,114.06],[291.541,114.815],[289.213,115.427],[284.5,116],[284.5,116],[282.204,115.889],[279.648,115.576],[275,114.53],[275,114.53],[272.982,113.687],[270.821,112.509],[267.1,109.77],[267.1,109.77],[265.635,108.184],[264.162,106.285],[261.87,102.5],[261.87,102.5],[261.107,100.393],[260.528,97.896],[260.019,92.25],[260.019,92.25],[260.15,89.287],[260.538,86.271],[261.98,80.75],[261.98,80.75],[262.973,78.434],[264.215,76.015],[266.81,72],[266.81,72],[268.26,70.465],[270.115,68.87],[274.08,66.25],[274.08,66.25],[276.22,65.326],[278.521,64.621],[283,64.019]]],[0,[[357,67.08],[357,67.08],[358.269,67.131],[359.87,67.323],[363.25,68.01],[363.25,68.01],[364.952,68.609],[366.818,69.516],[370.14,71.75],[370.14,71.75],[371.53,73.172],[373.002,75.015],[375.49,79],[375.49,79],[376.413,80.981],[377.275,83.057],[378.43,86.5],[378.43,86.5],[378.711,88.178],[378.941,90.53],[379.16,96],[379.16,96],[379.036,98.892],[378.693,101.789],[377.53,106.5],[377.53,106.5],[376.681,108.277],[375.582,110.16],[373.2,113.34],[373.2,113.34],[371.912,114.564],[370.409,115.803],[367.5,117.75],[367.5,117.75],[365.901,118.361],[363.767,118.869],[359,119.36],[359,119.36],[356.55,119.265],[353.942,118.982],[349.5,118.02],[349.5,118.02],[347.605,117.162],[345.403,115.85],[341.18,112.57],[341.18,112.57],[339.064,110.371],[337.463,108.182],[335.3,103],[335.3,103],[334.654,100.232],[334.291,97.5],[334.4,92],[334.4,92],[334.843,89.452],[335.581,86.576],[337.52,81.25],[337.52,81.25],[338.797,78.954],[340.434,76.587],[343.95,72.75],[343.95,72.75],[345.747,71.394],[347.713,70.108],[351.2,68.33],[351.2,68.33],[352.681,67.866],[354.268,67.476],[357,67.08]]]];
// Logo horizontal offset (> 0 - right, < 0 - left)
logo_x_offset = 0; // [-100:0.1:100]
// Logo vertical offset (> 0 - upper, < 0 - lower)
logo_y_offset = 0; // [-100:0.1:100]
// Logo scale in percentage of box size
logo_scale = 70; // [0:0.1:100]

/* [Hidden] */

function isArray(v) = len(v) != undef;
function sum(v, i=0, j=100500) = len(v) > i && i <= j ? v[i] + sum(v, i+1, j) : 0;

//if (isArray(deck_thicknesses)) deck_thicknesses = 1;
deck_height = sum(deck_thicknesses) + (len(deck_thicknesses) - 1) * deck_spacer;
e = .01;
walls = wall_thickness * 2;

module logo(h) {
	if (isArray(logo_data)) {
		s = max((deck_width + walls) / logo_data[0][0], (h + walls - lid_height) / logo_data[0][1]) * logo_scale / 100;
		
		minX = min([for(i=[1:len(logo_data) - 1]) min([for(j=[0:len(logo_data[i][1]) - 1]) logo_data[i][1][j][0]])]);
		minY = min([for(i=[1:len(logo_data) - 1]) min([for(j=[0:len(logo_data[i][1]) - 1]) logo_data[i][1][j][1]])]);

			translate([(deck_width + walls - logo_data[0][0] * s) / 2, (deck_length + walls - lid_height + logo_data[0][1] * s) / 2, 0]) scale([s, -s, 1]) translate([-minX, -minY, 0]) difference() {
			union() for (i = [1:len(logo_data) - 1] ) if (logo_data[i][0]==1) linear_extrude(height = h) polygon(logo_data[i][1]);
			translate([0, 0, -e]) for (i = [1:len(logo_data) - 1] ) if (logo_data[i][0]==0) linear_extrude(height = h + e * 2) polygon(logo_data[i][1]);
		}
	}
}

function halign(h) = h == "l"?"left":(h == "c"?"center":"right");

function valign(v) = v == "t"?"top":(v == "c"?"center":"baseline");

module textAndLogo() {
		text_1OffsetX = (text_1_align[0]=="l"?0:(text_1_align[0]=="c"?deck_width / 2 + wall_thickness:deck_width + walls)) + text_1_x_offset;
		text_1OffsetY = (text_1_align[1]=="t"?deck_length - lid_height + walls:(text_1_align[1]=="c"?(deck_length - lid_height) / 2 + wall_thickness:0)) + text_1_y_offset;
		
		translate([text_1OffsetX, engrave_depth, text_1OffsetY]) rotate(a = 90, v = [1, 0, 0]) linear_extrude(height = abs(engrave_depth) + e) text(text_1, halign = halign(text_1_align[0]), valign = valign(text_1_align[1]), size = text_1_size, font = (text_1_font=="***CUSTOM***"?text_1_custom_font:str(text_1_font, ":style=", text_1_font_style)));
		
		text_2OffsetX = (text_2_align[0]=="l"?0:(text_2_align[0]=="c"?deck_width / 2 + wall_thickness:deck_width + walls)) + text_2_x_offset;
		text_2OffsetY = (text_2_align[1]=="t"?deck_length - lid_height + walls:(text_2_align[1]=="c"?(deck_length - lid_height) / 2 + wall_thickness:0)) + text_2_y_offset;
		
		translate([text_2OffsetX, engrave_depth, text_2OffsetY]) rotate(a = 90, v = [1, 0, 0]) linear_extrude(height = abs(engrave_depth) + e) text(text_2, halign = halign(text_2_align[0]), valign = valign(text_2_align[1]), size = text_2_size, font = (text_2_font=="***CUSTOM***"?text_2_custom_font:str(text_2_font, ":style=", text_2_font_style)));
		
	translate([logo_x_offset, engrave_depth, logo_y_offset]) rotate(a = 90, v = [1, 0, 0]) logo(abs(engrave_depth) + e);
}

module box() {
	difference() {
		 if(enable_engrave)
		 {
			 if (engrave_depth < 0) union() {
				cube([deck_width + walls, deck_height + walls, deck_length + walls - gap]);
				translate([0, -engrave_depth + e, 0]) textAndLogo();
				if (mirror) rotate(a = 180, v = [0, 0, 1]) translate([-deck_width - walls, -deck_height - walls - engrave_depth + e, 0]) textAndLogo();
			} else difference() {
				cube([deck_width + walls, deck_height + walls, deck_length + walls - gap]);
				textAndLogo();
				if (mirror) rotate(a = 180, v = [0, 0, 1]) translate([-deck_width - walls, -deck_height - walls - e, 0]) textAndLogo();
			} 
		}
		else
		{
			cube([deck_width + walls, deck_height + walls, deck_length + walls - gap]);
		}
		translate([wall_thickness, wall_thickness, wall_thickness]) cube([deck_width, deck_height, deck_length + e]);
		translate([0, deck_height + walls, deck_length + walls]) rotate(a = 180, v = [1, 0, 0]) lid(1);
	}
    if (len(deck_thicknesses) > 1) for (i=[0:len(deck_thicknesses) - 2]) translate([wall_thickness, wall_thickness + sum(deck_thicknesses, 0, i) + i * deck_spacer, wall_thickness]) cube([deck_width, deck_spacer, deck_length]);
}

module lid(forDifference = false) {
	k = forDifference?1:-1;
	p = forDifference?1:0;
	difference() {
		translate([-e * p, -e * p, -e * p]) cube([deck_width + walls + 2 * e * p, deck_height + walls + 2 * e * p, lid_height + e]);
		translate([wall_thickness / 2 + gap / 2 * k, wall_thickness / 2 + gap / 2 * k, wall_thickness]) {
			cube([deck_width + wall_thickness - gap * k, deck_height + wall_thickness - gap * k, lid_height]);
		}
	}
}

if (part == "box") translate([-deck_width / 2 - wall_thickness, -deck_height / 2 - wall_thickness, 0]) box();
else if (part == "lid") translate([-deck_width / 2 - wall_thickness, -deck_height / 2 - wall_thickness, 0]) lid();
else {
	translate([-deck_width / 2 - wall_thickness, -deck_height - walls - 5, 0]) box();
	translate([-deck_width / 2 - wall_thickness, 5, 0]) lid();
}