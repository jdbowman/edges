nownum = floor(now+1);
ndays = 15
datadir = '/data1/edges/data/2014_February_Boolardy/';

for n=(nownum-ndays+1):nownum

  doy = floor(n) - datenum(year(n), 1, 0);
  
  disp(sprintf('%s%04d_%03d_*.acq', datadir, year(n), doy));
  drawnow('update');

  %edges_acq2waterfall(sprintf('%s%04d_%03d_*.acq', datadir, year(n), doy));
  edges_dailyweather(datadir, year(n), doy);

end

