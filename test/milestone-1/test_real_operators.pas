program ComputeSeries;

var
  i, n: integer;
  x, sum, term: real;

begin
  n := 10;
  x := 2.5;
  sum := 0.0;
  term := 1.0;

  i := 1;
  while i <= n do
  begin
    term := term * (x / i);
    sum := sum + term;

    if i mod 2 = 0 then
      sum := sum - (term / (i + 1))
    else
      sum := sum + (term / (i + 1));

    i := i + 1;
  end;

  if sum > 50.0 then
    sum := sum / 2.0
  else
    sum := sum * 2.0;

end.