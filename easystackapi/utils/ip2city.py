import ipdb

db = ipdb.District(r"C:\Users\cloud\Downloads\ipdb-python-master\ipipfree.ipdb")
print(db.find_map("123.14.90.47", "CN"))

# db = ipdb.District("/path/to/china_district.ipdb")
print(db.is_ipv4(), db.is_ipv6())
print(db.languages())
print(db.fields())
print(db.build_time())
print(db.find("122.112.155.122", "CN"))
print(db.find_info("132.155.122.123", "CN").country_name)