program TestArrayRange;
type
  MyArray = array[1 .. 100] of integer;
var
  Numbers: MyArray;
begin
  Numbers[1] := 10;
end.
