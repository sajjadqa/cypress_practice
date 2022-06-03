#! /bin/bash
environment=$1


./run_system_tests.py $environment web &
./run_system_tests.py $environment web &
./run_system_tests.py $environment web &
./run_system_tests.py $environment web &
./run_system_tests.py $environment web &
./run_system_tests.py $environment web &

./run_system_tests.py $environment api &
./run_system_tests.py $environment api &
./run_system_tests.py $environment api &
./run_system_tests.py $environment api &
./run_system_tests.py $environment api &
./run_system_tests.py $environment api &
./run_system_tests.py $environment api &
./run_system_tests.py $environment api &

wait
echo "system_under_load complete."
