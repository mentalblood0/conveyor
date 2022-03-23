import dataclasses
from ..Linker import Linker



@lambda c: c()
class LinkerFactory:

	def __call__(
		self,
		input_type,
		input_status,
		source_type,
		source_status,
		output_status,
		metadata_field
	):
		return type(
			'__'.join([
				'Linker',
				input_type,
				input_status,
				source_type,
				source_status,
				output_status,
				metadata_field
			]),
			(Linker,),
			{
				'input_type': input_type,
				'input_status': input_status,
				'source_type': source_type,
				'source_status': source_status,
				'output_status': output_status,
				'link': lambda self, item: dataclasses.replace(
					item,
					metadata={metadata_field: item.metadata[metadata_field]}
				)
			}
		)