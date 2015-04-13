function edges_dailyweather(datadir, year, doy)        

	disp(datadir);
	disp(sprintf('%d, %d', year, doy));
	drawnow('update')

	params.indir = datadir;
	params.inweather = [params.indir, '/weather.txt'];
	params.inthermal = [params.indir, '/thermlog.txt'];
	params.inwebcamdir = [params.indir, '/cameras'];
	params.outpath = '/data1/edges/live/';
	params.outname = sprintf('%04d_%03d', year, doy);
	params.outfile_webcam_1 = [params.outpath params.outname '_camera_1.webm'];
	params.outfile_webcam_2 = [params.outpath params.outname '_camera_2.webm'];
	params.outfile_webcam_3 = [params.outpath params.outname '_camera_3.webm'];
	params.outfile_weather = [params.outpath params.outname '_weather.png'];

	pad = 9/60/24/366; % pad the date range by 9 minutes to be sure to catch everything
	params.startdate = edgesdate([year, doy, 0, 0, 0])-pad;
	params.stopdate = edgesdate([year, doy, 23, 59, 59.99])+pad;

	disp('plotwebcam');drawnow('update');

	plotwebcam(params.inwebcamdir, 'camera_1.jpg', params.outfile_webcam_1, params.startdate, params.stopdate);
	plotwebcam(params.inwebcamdir, 'camera_2.png', params.outfile_webcam_2, params.startdate, params.stopdate);
	plotallskycamera(params.inwebcamdir, 'camera_3.png', params.outfile_webcam_3, params.startdate, params.stopdate);

	disp('plottemps');drawnow('update');
	plottemps(params.inweather, params.inthermal, params.outfile_weather, params.startdate, params.stopdate);

	disp('done');drawnow('update');
  
end
