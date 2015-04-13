
import u3
d = u3.U3()
d.configIO(FIOAnalog = 15)

d.setDOState(4, state = 1)      # inverse logic, all OFF
d.setDOState(5, state = 1)
d.setDOState(6, state = 1)
d.setDOState(7, state = 1)

d.close()
