
function Rp = gamma_shifted(S11, S12S21, S22, R)

Rp = S11 + (S12S21.*R./(1-S22.*R));

