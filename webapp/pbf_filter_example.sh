set -e
# Example for filtering osm.pbf file for relevant elements to generate AOIs
# for osmconvert and osmfilter command, run apt install osmctools in container

osmconvert planet-latest.osm.pbf --out-o5m > planet-latest.o5m

osmfilter planet-latest.o5m --keep="building= landuse=retail amenity=pub =bar =cafe =restaurant =pharmacy =bank =fast_food =food_court =ice_cream =library =ferry_terminal =clinic =doctors =hospital =pharmacy =veterinary =dentist =arts_centre =cinema =community_centre =casino =fountain =nightclub =studio =theatre =dojo =internet_cafe =marketplace =post_opffice =townhal shop=mall =bakery =beverages =butcher =chocolate =coffee =confectionery =deli =frozen_food =greengrocer =healthfood =ice_cream =pasta =pastry =seafood =spices =tea =department_store =supermarket =bag =boutique =clothes =fashion =jewelry =leather =shoes =tailor =watches =chemist =cosmetics =hairdresser =medical_supply =electrical =hareware =electronics =sports =swimming_pool =collector =games =music =books =gift =stationery =ticket =laundry =pet =tobacco =toy leisure=adult_gaming_centre =amusement_arcade =beach_resort =fitness_centre =garden =ice_rink =sports_centre =water_park" --drop="access=private =no"  --keep-tags="building= amenity= shop= leisure= access= type= landuse= " --keep-ways= --drop-tags="addr*=" --drop-author --keep="highway=" > planet-latest-pois.o5m

osmconvert planet-latest-pois.o5m --out-pbf > planet-latest-pois.osm.pbf

# cleanup
# rm planet-latest-pois.o5m
# rm planet_latest-o5m
