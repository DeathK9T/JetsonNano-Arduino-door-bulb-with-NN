import speech_recognition as sr

class Statement:
    def __init__(self, dict):
        self.confidence = dict['confidence']
        self.text = dict['transcript'].lower()

    def __repr__(self):
        return "[{}] {}".format(self.confidence, self.text)

    def __str__(self):
        return self.text

    def __gt__(self, other):
        return self.confidence > other.confidence

class Speech:
	def __init__(self, google_treshold = 0.5):
		self._recognizer = sr.Recognizer()
		self._microphone = sr.Microphone()
		self.google_treshold = google_treshold

	def json_to_statements(self, json):
		statements = []
		if len(json) is not 0:
			for dict in json['alternative']:
				dict['confidence'] = self.google_treshold + 0.1
			statements.append(Statement(dict))
		return statements

	def recognize(self, audio):
		statements = []
		try:
			json = self._recognizer.recognize_google(audio, language="ru_RU", show_all=True)
			statements = self.json_to_statements(json)
		except sr.UnknownValueError:
			print("[GoogleSR] Неизвестное выражение")
		except sr.RequestError as e:
			print("[GoogleSR] Не могу получить данные; {0}".format(e))
		return statements

	def choose_best_statement(self, statements):
		if statements:
			return max(statements, key=lambda s: s.confidence)
		else:
			return None

	def get_ambient(self):
		print('Get ambient')
		with self._microphone as source:
			self._recognizer.adjust_for_ambient_noise(source)

	def run(self):
		with self._microphone as source:
			audio = self._recognizer.listen(source)
		statements = self.recognize(audio)
		best_statement = self.choose_best_statement(statements)
		return best_statement
