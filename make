#!/usr/bin/env bash
logfile="err.log"
okfile="ok.ok"

rm $logfile > /dev/null 2>&1
rm $okfile  > /dev/null 2>&1

echo -e "mkvenv BEGIN:" >> $logfile  && \
./mkvenv env > >(tee -a    $logfile) && \
echo -e "mkvenv END:"   >> $logfile  && \

echo -e "install BEGIN:">> $logfile  && \
./install    > >(tee -a    $logfile) && \
echo -e "install END:"  >> $logfile  && \

touch $okfile

if [[ ! -e $okfile ]]; then
 echo "Install was not succesful. More info can be found in: err.log"
 exit 1
else
 echo "Installing done. Run with: rss"
 rm $logfile > /dev/null 2>&1
 rm $okfile  > /dev/null 2>&1
fi
