# Makefile for PciAcqPX14
# 	@g++ -Wall -g -std=c++0x $^ -o $(TARGET) -lsig_px14400 -lfftw3 -pthread


TARGET   := run_edges

.PHONY : clean distclean

$(TARGET) : *.cpp
	@echo "Building:   "$(TARGET)"..."
	@g++ -Wall -O3 -mtune=native -std=c++0x $^ -o $(TARGET)_double -lsig_px14400 -lfftw3 -pthread -lrt
	@g++ -Wall -O3 -mtune=native -std=c++0x $^ -o $(TARGET)_single -lsig_px14400 -lfftw3f -pthread -lrt -DFFT_SINGLE_PRECISION

	chmod u+s $(TARGET)_double
	chmod u+s $(TARGET)_single

clean :
	@echo "Cleaning: "$(TARGET)"..."
	@rm -f *~ *.o $(TARGET)_double $(TARGET)_single

