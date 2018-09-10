CREATE OR REPLACE VIEW building AS
	SELECT *
	FROM planet_osm_polygon
	WHERE building IS NOT NULL;

DROP TABLE IF EXISTS pois;
CREATE TABLE pois (
  id SERIAL PRIMARY KEY,
  geometry geometry
);

CREATE OR REPLACE VIEW pois_v AS (
  (SELECT way AS geometry FROM planet_osm_polygon
      WHERE (amenity = ANY(ARRAY['pub', 'bar', 'cafe', 'restaurant',
          'pharmacy', 'bank', 'fast_food', 'food_court', 'ice_cream',
          'library', 'ferry_terminal', 'pharmacy', 'arts_centre', 'cinema',
          'community_centre', 'casino', 'fountain', 'nightclub', 'studio',
          'theatre', 'internet_cafe', 'marketplace', 'post_office',
          'townhall'])

              OR shop = ANY(ARRAY['mall', 'bakery', 'beverages', 'butcher',
                'chocolate', 'coffee', 'confectionery', 'deli', 'frozen_food',
                'greengrocer', 'healthfood', 'ice_cream', 'pasta', 'pastry',
                'seafood', 'spices', 'tea', 'department_store', 'supermarket',
                'bag', 'boutique', 'clothes', 'fashion', 'jewelry', 'leather',
                'shoes', 'tailor', 'watches', 'chemist', 'cosmetics',
                'hairdresser', 'medical_supply', 'electrical', 'hardware',
                'electronics', 'sports', 'swimming_pool', 'collector', 'games',
                'music', 'books', 'gift', 'stationery', 'ticket', 'laundry',
                'pet', 'tobacco', 'toys'])

              OR leisure = ANY(ARRAY['adult_gaming_centre', 'amusement_arcade',
                'beach_resort', 'fitness_centre', 'ice_rink',
                'sports_centre', 'water_park'])

              OR landuse = ANY(ARRAY['retail']))

             AND access IS DISTINCT FROM 'private'

  UNION ALL

  (SELECT building.way AS geometry FROM building
      INNER JOIN planet_osm_point AS point
          ON ST_Within(point.way, building.way)
      WHERE (point.amenity = ANY(ARRAY['pub', 'bar', 'cafe', 'restaurant',
          'pharmacy', 'bank', 'fast_food', 'food_court', 'ice_cream',
          'library', 'ferry_terminal', 'pharmacy', 'arts_centre', 'cinema',
          'community_centre', 'casino', 'fountain', 'nightclub', 'studio',
          'theatre', 'internet_cafe', 'marketplace', 'post_office',
          'townhall'])

              OR point.shop = ANY(ARRAY['mall', 'bakery', 'beverages', 'butcher',
                'chocolate', 'coffee', 'confectionery', 'deli', 'frozen_food',
                'greengrocer', 'healthfood', 'ice_cream', 'pasta', 'pastry',
                'seafood', 'spices', 'tea', 'department_store', 'supermarket',
                'bag', 'boutique', 'clothes', 'fashion', 'jewelry', 'leather',
                'shoes', 'tailor', 'watches', 'chemist', 'cosmetics',
                'hairdresser', 'medical_supply', 'electrical', 'hardware',
                'electronics', 'sports', 'swimming_pool', 'collector', 'games',
                'music', 'books', 'gift', 'stationery', 'ticket', 'laundry',
                'pet', 'tobacco', 'toys'])

              OR point.leisure = ANY(ARRAY['adult_gaming_centre',
                'amusement_arcade', 'beach_resort', 'fitness_centre',
                'ice_rink', 'sports_centre', 'water_park'])

              OR point.landuse = ANY(ARRAY['retail']))

          AND point.access IS DISTINCT FROM 'private')

  UNION ALL

  (SELECT ST_Buffer(point.way, 5, 1) AS geometry FROM building
      RIGHT JOIN planet_osm_point AS point
          ON st_within(point.way, building.way)
      WHERE (point.amenity = ANY(ARRAY['pub', 'bar', 'cafe', 'restaurant',
          'pharmacy', 'bank', 'fast_food', 'food_court', 'ice_cream',
          'library', 'ferry_terminal', 'pharmacy', 'arts_centre', 'cinema',
          'community_centre', 'casino', 'fountain', 'nightclub', 'studio',
          'theatre', 'internet_cafe', 'marketplace', 'post_office',
          'townhall'])

              OR point.shop = ANY(ARRAY['mall', 'bakery', 'beverages', 'butcher',
                'chocolate', 'coffee', 'confectionery', 'deli', 'frozen_food',
                'greengrocer', 'healthfood', 'ice_cream', 'pasta', 'pastry',
                'seafood', 'spices', 'tea', 'department_store', 'supermarket',
                'bag', 'boutique', 'clothes', 'fashion', 'jewelry', 'leather',
                'shoes', 'tailor', 'watches', 'chemist', 'cosmetics',
                'hairdresser', 'medical_supply', 'electrical', 'hardware',
                'electronics', 'sports', 'swimming_pool', 'collector', 'games',
                'music', 'books', 'gift', 'stationery', 'ticket', 'laundry',
                'pet', 'tobacco', 'toys'])

              OR point.leisure = ANY(ARRAY['adult_gaming_centre',
                'amusement_arcade', 'beach_resort', 'fitness_centre',
                'ice_rink', 'sports_centre', 'water_park'])

              OR point.landuse = ANY(ARRAY['retail']))

          AND point.access IS DISTINCT FROM 'private'
          AND building.way IS NULL)
));

INSERT INTO pois(geometry) (
  SELECT geometry
  FROM pois_v
);
