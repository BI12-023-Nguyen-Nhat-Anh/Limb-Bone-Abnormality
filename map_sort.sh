TOOLS_PATH="/home/student10"
picard="$TOOLS_PATH/picard-tools-1.119"
bwa="bwa"
java="java"
humanref="/storage/student10/hg38.fa.gz"
sample_id=$1
read1=${sample_id}_1.paired.fastq
read2=${sample_id}_2.paired.fastq


echo "==============="
echo "MAPING WITH BWA"
echo "==============="

$bwa mem -t 10 $humanref $read1 $read2 > ${sample_id}.sam 

echo "================"
echo "SORT WITH PICARD"
echo "================"

$java -Xmx32G -jar $picard/SortSam.jar \
I=${sample_id}.sam \
O=${sample_id}.sort.bam \
SORT_ORDER=coordinate \
CREATE_INDEX=true \
TMP_DIR="/home/student10/tmp" \
VALIDATION_STRINGENCY=SILENT
status=$?
echo "Status: $status" > test.txt