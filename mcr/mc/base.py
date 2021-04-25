from mcr.mc.properties import _JsonProperty


class JsonDict(dict):
	def __init__(self, json_dict: dict = None):
		if json_dict is None:
			return
			
		auto = []
		for value in self.__class__.__dict__.values():
			if isinstance(value, _JsonProperty):
				if value.key in json_dict:
					self[value.key] = value.init(json_dict[value.key])
					auto.append(value.key)

		for value in self.__class__.__base__.__dict__.values():
			if isinstance(value, _JsonProperty):
				if value.key in json_dict:
					self[value.key] = value.init(json_dict[value.key])
					auto.append(value.key)

		manual = []
		for key, value in json_dict.items():
			if key not in self:
				self[key] = value
				manual.append(key)