from common.asset_class import Asset

assets = {}

def parse_assets(name, sizeside, base_value):
    if name in assets:
        assets[name].add(sizeside,base_value)
    else:
        assets[name] =  Asset(name,sizeside,base_value)
