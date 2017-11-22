function [controller_data, weather_data] = plottemps(filename1, filename2, outfile, startdate, stopdate)  
% Weather log file
% Controller log file
% Output filename
% start date in edgesdate format
% stop date in edgesdate format
 
  nchunk = 2000;
  weather_data = zeros(4, nchunk);
  controller_data = zeros(4, nchunk);
  
  % Read the weather.txt file
  n = 0;
  fid = fopen(filename1, 'r');
  while 1
    line = fgets(fid);
    nLine = length(line);
    if (~ischar(line) || length(line)==0)
      break;
    end
    
    % Parse the line
    try 
      [linevals, count, errmsg, index] = ...
        sscanf(line, '%g:%g:%g:%g:%g rack_temp %g Kelvin, ambient_temp %g Kelvin, ambient_hum %g percent', 8);  
    catch
      % Uh oh, we probably have an incomplete file.
      disp(sprintf('Error: Failed to parse line in weather file.', n));              
      break;
    end 
    
    this_date = edgesdate(linevals(1:5));
    if (this_date <= stopdate)
      if (this_date >= startdate)
        % keep for plot
        n = n + 1;
        if (mod(n, nchunk)==0)
          newweather = zeros(size(weather_data) + [0 nchunk]);
          newweather(:,1:n) = weather_data;
          weather_data = newweather;
        end
        weather_data(:,n) = [this_date, linevals(6:8)'];
        
      end
    else
      break;
    end
  end % while
  fclose(fid);
  
  bHaveWeatherData = 0;
  if (n>0)
    weather_data = weather_data(:,1:n);
		weather_data(2:3,:) = weather_data(2:3,:) - 273.15;
		[row, col] = find(abs(weather_data(2:end, :)) > 110);
		weather_data(row+1, col) = NaN;
    bHaveWeatherData = 1;
  end
  

  % --------------------
  % READ CONTROLLER DATA
  % --------------------
  
  n=0;
  fid = fopen(filename2, 'r');
  while 1
    line = fgets(fid);
    nLine = length(line);
    if (~ischar(line) || length(line)==0)
      break;
    end
    
    % Parse the line
    try 
      [linevals, count, errmsg, index] = ...
        sscanf(line, '%g:%g:%g:%g:%g temp_set %g deg_C tmp %g deg_C pwr %g percent', 8);  
    catch
      % Uh oh, we probably have an incomplete file.
      disp(sprintf('Error: Failed to parse line in controller file.', nta));              
      break;
    end 
    
    this_date = edgesdate(linevals(1:5));
    if (this_date <= stopdate)
      if (this_date >= startdate)
        % keep for plot
        n = n + 1;
        if (mod(n, nchunk)==0)
          newcontroller = zeros(size(controller_data) + [0 nchunk]);
          newcontroller(:,1:n) = controller_data;
          controller_data = newcontroller;
        end
        controller_data(:,n) = [this_date, linevals(6:8)'];       
      end
    else
      break;
    end
  end % while
  fclose(fid);
  
  bHaveControllerData = 0;
  if (n>0)
    controller_data = controller_data(:,1:n);
		[row, col] = find(controller_data(2:end, :) > 110);
		controller_data(row+1, col) = NaN;
    bHaveControllerData = 1;
  end
  

  % ----------
  % Make plots
  % ----------
  
  figure(1);clf;
	set(gcf, 'visible', 'off');
  

  hold on;
  
  if (bHaveWeatherData)  
	  x = 366.*(weather_data(1,:)-floor(startdate));
    plot(x, weather_data(2,:), 'b-', 'DisplayName', ' Rack temp');
    plot(x, weather_data(3,:), 'r-', 'DisplayName', 'Ambienttemp');
    plot(x, weather_data(4,:).*55./210+27.5, 'g--', 'DisplayName', 'Rel. humidity (%)');
  end
  if (bHaveControllerData)
    xx = 366.*(controller_data(1,:)-floor(startdate));
    plot(xx, controller_data(2,:), 'k:', 'DisplayName', 'Cntrl set temp');
    plot(xx, controller_data(3,:), 'k-', 'DisplayName', 'Cntrl actual tmp');
    plot(xx, controller_data(4,:).*55./210+27.5, 'm--', 'DisplayName', 'Cntrl power (%)'); 
  end
  hold off;
  
 	limx = 366.*([startdate stopdate] - floor(startdate));
	xlim(limx);
  ylim([0 55]);
  xlabel('DOY (UTC)');
  ylabel('Temperature (degC)');
  
  %   legend('Rack temp', 'Ambient temp', 'Rel. humidity (%)','Cntrl set temp', 'Cntrl actual temp', 'Cntrl power (%)');
  legend('show');
  legend('boxoff');
  title('Temperature and Power Levels');
  ax1 = gca;
  set(ax1, 'YAxisLocation', 'left');
  set(ax1, 'box', 'off');
  ax2 = axes('Position',get(ax1,'Position'),...
           'XAxisLocation','top',...
           'YAxisLocation','right',...
           'XTickLabel', {},...
           'Color','none');
  xlim(limx);
  ylim([-105 105]);
  ylabel('Percent, %');

  print(outfile, '-dpng', '-r108');


end
    
    
