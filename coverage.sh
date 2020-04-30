sed -En 's@Statements.*: @@p' ./ci_frontend.log | sed -n 's@%.*@@p'  > coverage_frontend.log
