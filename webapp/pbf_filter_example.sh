# Example for filtering osm.pbf file for relevant elements to generate AOIs
# this does not yet include streets for the network centrality!
# for osmconvert and osmfilter command, run apt install osmctools in container

osmconvert switzerland-latest.osm.pbf --out-o5m > switzerland-latest.o5m

# filter without streets for network centrality
osmfilter switzerland-latest.o5m --keep="building= landuse=retail amenity=pub =bar =cafe =restaurant =pharmacy =bank =fast_food =food_court =ice_cream =library =ferry_terminal =clinic =doctors =hospital =pharmacy =veterinary =dentist =arts_centre =cinema =community_centre =casino =fountain =nightclub =studio =theatre =dojo =internet_cafe =marketplace =post_opffice =townhal shop=mall =bakery =beverages =butcher =chocolate =coffee =confectionery =deli =frozen_food =greengrocer =healthfood =ice_cream =pasta =pastry =seafood =spices =tea =department_store =supermarket =bag =boutique =clothes =fashion =jewelry =leather =shoes =tailor =watches =chemist =cosmetics =hairdresser =medical_supply =electrical =hareware =electronics =sports =swimming_pool =collector =games =music =books =gift =stationery =ticket =laundry =pet =tobacco =toy leisure=adult_gaming_centre =amusement_arcade =beach_resort =fitness_centre =garden =ice_rink =sports_centre =water_park" --drop="access=private =no" > switzerland-latest-pois.o5m

osmconvert switzerland-latest-poits.o5m --out-pbf > switzerland-latest-pois.osm.pbf
