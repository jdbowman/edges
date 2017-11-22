function plotallskycamera(dirname, search_string, outfile, startdate, stopdate)  
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
	pad = 10/60/24/366;
	ind = find(dates>(startdate-pad) & dates<(stopdate+pad));

	if (~isempty(ind))

		tmpfile = [tempname '_matlab_allsky.avi'];
		writerObj = VideoWriter(tmpfile, 'Uncompressed AVI');
		writerObj.FrameRate = 6;
		open(writerObj);

		last_p = [-1 -1];
		for ii=1:length(ind)

			im = imread([dirname '/' names{ind(ii)}]);
			im = im2double(imcrop(im, [300, 90, 860, 860]));

			% Find the pixel values of the 5 and 95% brightness levels.
			p = prctile(im(:),[5 95]);

			% Keep the night images from being stretched so much that the noise is visible
			p(2) = max(p(2), 0.055); 

			% The lower limit is almost always the same, so let's just make it constant
			p(1) = 0.03;

			% Limit the rate that p can change
			if (last_p(1) > -1)
				factor = 0.3;
				p = (factor.*p + (1-factor).*last_p);
			end
			last_p = p;

			% Apply the pixel scaling to make all images visible.
			im = (im-p(1))/(p(2)-p(1));
			im(im<0)=0;
			im(im>1)=1;

		%figure(1);imshow(im);title(sprintf('%s:  [%f, %f]', names{ind(ii)}, p(1), p(2)));drawnow;pause(1);
			writeVideo(writerObj, im);

		end
		
		close(writerObj);
		
		% Convert the file to webm	
		cmdav = ['cd ' dirname '; mencoder ' tmpfile ' -of lavf -lavfopts format=webm -ovc lavc -lavcopts mbd=2:trell:v4mv:vcodec=libvpx -ffourcc VP80 -o ' outfile];
	
		cmdav

		% Execute command to make webm movie
		[status, cmdout] = system(cmdav, '-echo');

		% Cleanup the temporary file
		delete(tmpfile);

	end
  
end
    
    
