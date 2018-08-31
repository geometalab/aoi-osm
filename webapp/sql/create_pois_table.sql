DROP TABLE IF EXISTS pois;

CREATE TABLE pois (
	id SERIAL PRIMARY KEY,
	geometry geometry,
);

-- Note that building filters some pois such as sports_centre because sports 
-- centre is not a building
CREATE OR REPLACE VIEW building AS
	SELECT *
	FROM planet_osm_polygon AS building
	WHERE (
		building IS NOT NULL
		AND access IS DISTINCT FROM 'private'
	);
		
INSERT INTO pois(geometry, osm_id, is_node) (
	SELECT way, pois_subquery.osm_id, pois_subquery.is_node
	FROM (
		SELECT
			CASE 
				WHEN building.way IS NULL THEN point.way
				ELSE building.way
			END, point.amenity, point.shop, point.leisure, 
			point.landuse, point.access
		FROM building RIGHT JOIN planet_osm_point AS point 
		ON ST_Within(point.way, building.way)
		
		UNION ALL
		
		SELECT way AS geometry, amenity, shop, leisure, landuse, "access"
		-- Note that building filters some pois such as sports_centre 
		-- because sports centre is  not a building that's why 
		-- planet_osm_polygon is used instead
		FROM planet_osm_polygon

	)AS pois_subquery
	
	WHERE (
		amenity = ANY(ARRAY['pub', 'bar', 'cafe', 'restaurant',
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

		OR leisure = ANY(ARRAY['adult_gaming_centre',
		'amusement_arcade', 'beach_resort', 'fitness_centre',
		'ice_rink', 'sports_centre', 'water_park'])

		OR landuse = ANY(ARRAY['retail'])
	) 
	
	AND "access" IS DISTINCT FROM 'private'
);

CREATE INDEX pois_geometry ON pois USING gist(geometry);

