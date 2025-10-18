program TestOperators;
var
  a, b: integer;
  c, d: boolean;
begin
  a := 10;
  b := 20;
  c := (a < b) and (b > a);
  d := (a <> b) or not c;
  if (a <= b) and (b >= a) then
    a := 0;
end.