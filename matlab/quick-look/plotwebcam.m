function plotwebcam(dirname, search_string, outfile, startdate, stopdate)  
% Full path to directory containing webcam images
% Output filename
% start date in edgesdate format
% stop date in edgesdate format

	files = dir([dirname '/*' search_string]);
	names = {files.name};
	dates = zeros(1, length(names));

	for n=3:(length(names)-1)

		[ydhm] = sscanf(names{n}, '%d_%d_%d_%d');
		dates(n) = edgesdate([ydhm; 0]);

	end

	% Find dates in the range of the data file
	ind = find(dates>startdate & dates<stopdate);

	if (~isempty(ind))

		if (0)
			% OLD OLD OLD
			% Construct cat command
			cmdcat = 'cat ';
			for ii = 1:length(ind)
				cmdcat = [cmdcat, ' ', dirname, '/', names{ind(ii)}];
			end
		
			% Construct avconv command string
			cmdav = [cmdcat, ' | avconv -y -r 3 -f image2pipe -vcodec mjpeg -i - -f webm -c:v libvpx -an -qmin 1 -qmax 4 ', outfile];
		else

			filelist = sprintf('%s,', names{ind});
			filelist = filelist(1:(end-1) );
			singlefile = names{ind(1)};
			suffix = singlefile((end-2):end);
		
			cmdav = ['cd ' dirname '; mencoder mf://' filelist ' -mf fps=6:type=' suffix ' -of lavf -lavfopts format=webm -ovc lavc -lavcopts mbd=2:trell:v4mv:vcodec=libvpx -ffourcc VP80 -o ' outfile];
	
		end

		cmdav

		% Execute command to make webm movie
		[status, cmdout] = system(cmdav, '-echo');

	end
  
end
    
    
