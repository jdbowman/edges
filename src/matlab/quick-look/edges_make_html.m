livedir = '/data1/edges/live/';
files = dir([livedir '*_Ta.png']);
files_0 = dir([livedir '*_p0.png']);
files_1 = dir([livedir '*_p1.png']);
files_2 = dir([livedir '*_p2.png']);
files_power = dir([livedir '*_power.png']);
files_rfi = dir([livedir '*_rfi.png']);

nfiles = length(files);

fid1 = fopen([livedir 'index1_old.php'], 'w');
fid2 = fopen([livedir 'index_old.php'], 'w');

header1 = [ ...
  '<?php include("../header.htm"); ?>\n' ...
  '<h2>EDGES daily antenna spectra</h2>\n' ...
  '<p>X-axis: Frequency from 0 to 500 MHz (left to right)<br>\n' ...
  'Y-axis: UTC from 0 to 24 hours (bottom to top), unless data dropouts<br>\n' ...
  'Color: Log_10 [P_antenna],  Blue is <= 8, Red is >= 15 counts</p>\n' ...
  '<p><a href="index.php">List all antenna and ancillary plots by date</a></p>\n<p>\n'];

header2 = [ ...
  '<?php include("../header.htm"); ?>\n' ...
  '<h2>EDGES daily quick-look plots</h2>\n' ...
  '<p>X-axis: Frequency from 0 to 200 MHz (left to right)<br>\n' ...
  'Y-axis: UTC from 0 to 24 hours (bottom to top), unless data dropouts<br>\n' ...
  '<p><a href="index1.php">Show all antenna plots on one page</a></p>\n<p>\n'];

footer1 = ['</p>\n&nbsp;\n<?php include("../footer.htm"); ?>\n'];
footer2 = ['</p>\n\n<?php include("../footer.htm"); ?>\n'];

fprintf(fid1, header1);
fprintf(fid2, header2);


for n=nfiles:-1:1
  
  year = str2double(files(n).name(1:4));
  doy = str2double(files(n).name(6:8));
  date = doy2date(doy, year);
  
  thisfile = files(n).name;
  thisbase = thisfile(1:(end-7));
 
  fprintf(fid1, [files(n).name ' (' datestr(date, 1) ')<br>\n']);
  fprintf(fid1, ['<img src="' thisfile '" width="860" height="430"><br>\n']);
  
  fprintf(fid2, [thisfile(1:11) ' (' datestr(date, 1) ') ']);
  fprintf(fid2, ['&nbsp; <a href="' thisfile '">spec</a> ']);
  fprintf(fid2, ['&nbsp; <a href="' thisbase '_p0.png">p0 (antenna)</a>']);
  fprintf(fid2, ['&nbsp; <a href="' thisbase '_p1.png">p1 (ambient)</a>']);
  fprintf(fid2, ['&nbsp; <a href="' thisbase '_p2.png">p2 (hot)</a>']);
  fprintf(fid2, ['&nbsp; <a href="' thisbase '_rfi.png">RFI</a>']);
  fprintf(fid2, ['&nbsp; <a href="' thisbase '_power.png">power</a>']);
  
  if (exist([livedir thisbase '_temps.png'], 'file'))
    fprintf(fid2, ['&nbsp; <a href="' thisbase '_temps.png">thermal</a>']);
	end

  if (exist([livedir thisbase '_webcam.webm'], 'file'))
    fprintf(fid2, ['&nbsp; <a href="' thisbase '_webcam.webm">cam</a>']);
  end
	
	fprintf(fid2, '<br>\n');
	
  
end

fprintf(fid1, footer1);
fprintf(fid2, footer2);

fclose(fid1);
fclose(fid2);



