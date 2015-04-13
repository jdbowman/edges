function [s f]=s11read(file)

%[s f]=s11read(file)
%
s=read(rfdata.data,file);
[s f]=extract(s,'S_PARAMETERS');
s=s(1,1,:);
s=s(:);
