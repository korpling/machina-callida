x=$(sed -En 's@.*Statements.*: @@p' ./ci_frontend.log | sed -n 's@%.*@@p')
y=$(sed -En 's@TOTAL *[0-9]+ *[0-9]+ *@@p' ./ci_backend.log | sed -n 's@%.*@@p')
z=$(echo "scale=2; ($x + $y) / 2" | bc -l)
echo "Statements : ${z}%" > coverage.log
