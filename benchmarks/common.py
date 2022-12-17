from sharpener_lite import units



class OutputIsRun:

	@property
	def output(self):
		return self.run()


class WithOutputMetrics(OutputIsRun):

	@property
	def metric_size(self):
		return len(self.input_) * units.byte

	@property
	def metric_speed(self):
		return (self.metric_size / self.metric_mean_time).to(units.megabyte / units.second)