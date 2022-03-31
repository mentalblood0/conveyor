def composeSequence(functions):

	def new_f(*args, **kwargs):
		
		for f in functions[:-1]:
			f(*args, **kwargs)
		
		return functions[-1](*args, **kwargs)
	
	return new_f


class Effect:

	def install(self, target: any, *args, **kwargs):

		for name in dir(self):
			if (
				not name.startswith('__')
				and name != 'install'
			):

				field = getattr(self, name)

				if callable(field):
					setattr(target, name, composeSequence([
						field,
						getattr(target, name)
					]))
