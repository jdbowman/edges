function edges_acq2waterfall(filename, varargin)        
  % filename
  % nskip
  % outdim
  % outlim
  % outfile
    
  [inpath, inname, inext] = fileparts(filename);
  files = dir(filename);

  if length(files) ==0
    disp('edges_acq2waterfall:  No files so stopping.');
    return;
  end
    
  bWriteEach = 0;
  if (length(files) > 1)
    if (nargin < 5 || isempty(varargin{4}))
      % More than one input file found and output filename IS NOT specified
      disp('More than one input file found and no output filename specified.');
      disp('Using default output filenames and writing separate output files for each input file.');
      bWriteEach = 1;
    else
      % More than one input file found and output filename IS specified
      disp('More than one input file found and output filename is specified.');
      disp('Writing one merged output file containing all inputs.');
      bWriteEach = 0;
      params.outfile = varargin{4};
    end
  elseif (length(files) == 1)
    if (nargin < 5 || isempty(varargin{4}))
      % One input file found and output filename IS NOT specified
      disp('One input file found and no output filename specified.');
      disp('Using default output filename.');
      bWriteEach = 1;
    else
      % Oone input file found and output filename IS specified
      disp('One input file found and no output filename specified.');
      disp('Using specified output filename.');
      bWriteEach = 0;
      params.outfile = varargin{4};
    end
  else
    % No input file found
    disp('Error: No input file found');
    return;
  end
        

  if (nargin < 4 || isempty(varargin{3}))
      params.outlim = [180 1800];
  end
  if (nargin < 4 || isempty(varargin{2}))
      params.outdim = [960 480];
  end
  if (nargin < 2 || isempty(varargin{1}))
      params.nskip = 0;%27853; % Start at 85 MHz (assuming 65k channels)
  end
    
%  matlabpool open 8;

    for n=1:length(files)
      
      thisfile = [inpath '/' files(n).name];
    
      if (bWriteEach==1)
        [params.inpath, params.inname] = fileparts(thisfile);
        params.outpath = '/data1/edges/live/';
        params.outfile = [params.outpath params.inname '_Ta.png'];
        params.outfile_0 = [params.outpath params.inname '_p0.png'];
        params.outfile_1 = [params.outpath params.inname '_p1.png'];
        params.outfile_2 = [params.outpath params.inname '_p2.png'];
        params.outfile_power = [params.outpath params.inname '_power.png'];
        params.outfile_rfi = [params.outpath params.inname '_rfi.png'];
        params.outfile_temps = [params.outpath params.inname '_temps.png'];
        params.outfile_webcam = [params.outpath params.inname '_webcam.webm'];
      end

   
      disp(sprintf('Importing: %s', thisfile));

      if (bWriteEach == 1 || n == 1)
        params.tcal = 400;
        params.tload = 300;
        params.nchannels = 16384*2;
        params.nspec = params.nchannels-params.nskip;
        max_freq = 200;
        fstep = max_freq/params.nchannels;
        params.freqs = 0:fstep:(max_freq-fstep);
        params.freqs = params.freqs((params.nskip+1):end);
        nta = 0; 
        nanc = 13;
        line_ancillary = zeros(1,nanc);
        nchunk = 2000;
        dates = zeros(1,nchunk);
        waterfall = zeros(params.nspec, nchunk);
        waterfall_0 = zeros(params.nspec, nchunk);
        waterfall_1 = zeros(params.nspec, nchunk);
        waterfall_2 = zeros(params.nspec, nchunk);
      end
    
    bSpec = 0;
    nLine = 0;
    fid = fopen(thisfile, 'r');
    while 1
        % Read lines
        if (bSpec)
          if (nLine > 0)
            % fgets is too slow on big lines, so we have a hack using fread
            line = fread(fid, nLine, '*char');
          else
            % This is the first time we are reading a line containing a spectrum
            % and need to get its size
            line = fgets(fid);
            nLine = length(line); 
          
          end
          bSpec = 0;
        else
          line = fgets(fid);
          bSpec = 1;
        end
        
        if (~ischar(line) || length(line)==0)
            break;
        end
        
        if ((line(1) ~= '*') & (line(1) ~= '\n') & (line(1) ~= '#'))

            % Read the ancillary info
            try 
              [line_ancillary(1:10), count, errmsg, index] = sscanf(line, '%g:%g:%g:%g:%g %g %g %g %g %g spectrum ', 10);  
            catch
              
              % Uh oh, we probably have an incomplete file.
              disp(sprintf('Error: Failed to parse ancillary data at spectrum# %d', nta));              
              break;
             
            end             
              
            % Read the spectrum
            spec = decode(line((index+params.nskip*4):end));
            total_power = sum(spec);

	    if (length(spec) < params.nspec)
	        % Uh oh, we we probably have an incomplete file.
		disp(sprintf('Error: Failed to parse spectrum at # %d', nta));
		break;
	    end
    
            % Check the switch state and act accordingly
            swpos = line_ancillary(6);
            switch(swpos)
                case 0
                    p0 = spec;
                    ancillary = line_ancillary;
                    ancillary(11) = total_power;
                case 1
                    p1 = spec;
                    ancillary(12) = total_power;
                case 2
                    p2 = spec;
                    
                    if ((length(p0) == length(p1)) && (length(p0) == length(p2)) && (length(p1) == length(p2)))         
                      
                      ancillary(13) = total_power;
                      ta = (p0-p1) ./ (p2-p1) .* params.tcal + params.tload;
                      
                      nta = nta + 1;
                      if (mod(nta, nchunk)==0)
                        
                        newdates = zeros(size(dates) + [0 nchunk]);
                        newdates(:,1:nta) = dates;
                        dates = newdates;
                        
                        newfall = zeros(size(waterfall) + [0 nchunk]);
                        newfall(:,1:nta) = waterfall;
                        waterfall = newfall;
                        
                        newfall_0 = zeros(size(waterfall_0) + [0 nchunk]);
                        newfall_0(:,1:nta) = waterfall_0;
                        waterfall_0 = newfall_0;
                        
                        newfall_1 = zeros(size(waterfall_1) + [0 nchunk]);
                        newfall_1(:,1:nta) = waterfall_1;
                        waterfall_0 = newfall_0;
                        
                        newfall_2 = zeros(size(waterfall_2) + [0 nchunk]);
                        newfall_2(:,1:nta) = waterfall_2;
                        waterfall_2 = newfall_2;
                        
                      end
                      
                      dates(:,nta) = edgesdate(ancillary(1:5));
                      waterfall(:,nta) = ta;
                      waterfall_0(:,nta) = p0;
                      waterfall_1(:,nta) = p1;
                      waterfall_2(:,nta) = p2;
                      
                      if (mod(nta,100)==0)
                        disp(sprintf('%04d:%03d:%02d:%02d:%02d - line=%d', ancillary(1:5), nta));
                      end
                    else
                      % Uh oh, we probably have an incomplete file.
                      disp(sprintf('Error: Failed to calibrate at spectrum# %d', nta));
                      break;
                    end
            end
        end
    end
    
    fclose(fid);
    
    % Do some additional metrics and write to the disk the current waterfall (if it exists)
    if (bWriteEach == 1 && nta > 0)
      do_plots(params, dates(:,1:nta), waterfall(:,1:nta), waterfall_0(:,1:nta), waterfall_1(:,1:nta), waterfall_2(:,1:nta));
 %         save('/data1/edges/working/current.mat', 'dates', 'waterfall', 'waterfall_0', 'waterfall_1', 'waterfall_2', 'params');

    end
  
  end % loop through all files  

%  matlabpool close;
     
  % Write to the disk the current waterfall (if it exists)
  if (bWriteEach == 0 && nta > 0)
    do_plots(params, dates(:,1:nta), waterfall(:,1:nta), waterfall_0(:,1:nta), waterfall_1(:,1:nta), waterfall_2(:,1:nta));
%    save('/data1/edges/working/current.mat', 'dates', 'waterfall', 'waterfall_0', 'waterfall_1', 'waterfall_2', 'params');
  end

  disp(sprintf('Done. %d lines processed', nta));
    
end

function do_plots(params, dates, wf, wf0, wf1, wf2)

  xdim = size(wf, 1);
  ydim = size(wf, 2);
  
  write_waterfall(params.outfile, wf, params.outdim, params.outlim);
	write_waterfall(params.outfile_0, 10.*log10(wf0), params.outdim, [-90 -75]);
	write_waterfall(params.outfile_1, 10.*log10(wf1), params.outdim, [-90 -75]);
	write_waterfall(params.outfile_2, 10.*log10(wf2), params.outdim, [-90 -75]);
      
  plottemps(...
    [params.inpath, '/weather.txt'], ...
    [params.inpath '/thermlog.txt'], ...
    params.outfile_temps, ...
    dates(1), ...
    dates(end) );

% plotwebcam(...
%		[params.inpath, '/cameras'], 
%		'camera_1.jpg', ...
%		params.outfile_webcam, ...
%		dates(1), ...
%		dates(end) );
  
	% Find RFI - Loop over waterfall plot and remove polynomial from each spectrum
	rfi_npoly = 25;
	rfi_threshold = 5;
	rfi_range = find(params.freqs>45);
	rfi = zeros(size(wf));
	mask = ones(size(wf));
        
  for a=1:ydim %parfor
    %disp(sprintf('line: %d', a));
    [rfi(rfi_range,a) mask(rfi_range,a)] = fit_polynomial(wf(rfi_range,a), rfi_npoly, rfi_threshold, 0);
  end
  
	write_waterfall(params.outfile_rfi, (1-mask).*rfi, params.outdim, [0 100]);
      
	% Plot total power
	figure(1);clf;
	set(gcf, 'visible', 'off');

	[nr nc] = find(isnan(wf));
	goodr = setdiff(find(params.freqs>45), nr);
	total_ta = 10.*log10(mean(wf(goodr, :), 1));
	total_0 = 90 + 10.*log10(mean(wf0(params.freqs>45, :), 1));
	total_1 = 90 + 10.*log10(mean(wf1(params.freqs>45, :), 1));
	total_2 = 90 + 10.*log10(mean(wf2(params.freqs>45, :), 1));

	x = 366.*(dates - floor(dates(1)));
  plot(x, total_ta, 'k-', x, total_0, 'g-', x, total_1, 'b-', x, total_2, 'r-');
  xlim([x(1) x(end)]);
  xlabel('DOY [UTC]');
  ylim([0 51]);
  ylabel('Total Power [dB]');
  title('Total Power Above 50 MHz');
	legend('T_A', 'P0', 'P1', 'P2');        
  print(params.outfile_power, '-dpng', '-r108');
	
end
  

function write_waterfall(outfile, waterfall, outdim, outlim)

  % Plot the waterfall and save to PNG file
  pw = imresize(waterfall, outdim);
  lpw = pw;%log10(pw);
  minpw = outlim(1);%log10(outlim(1)); %2.25; %min(lpw(:));
  maxpw = outlim(2);%log10(outlim(2)); %3.25; %max(lpw(:));
  imwrite(uint8(256.*(lpw'-minpw)./(maxpw-minpw)), jet(256), outfile);

end


        








