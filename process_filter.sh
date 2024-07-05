#!/bin/bash
sample_id=$1
TOOLS_PATH="/home/student10"
java="java"
picard="$TOOLS_PATH/picard-tools-1.119"
gatk="$TOOLS_PATH/gatk/gatk-4.1.2.0/gatk"

echo "==================="
echo "FIXMATE WITH PICARD"
echo "==================="

$java -Xmx32G -jar $picard/FixMateInformation.jar \
I=${sample_id}.sort.bam \
O=${sample_id}.sort.fixmate.bam \
SORT_ORDER=coordinate \
CREATE_INDEX=true \
TMP_DIR="/home/student10/tmp" \
VALIDATION_STRINGENCY=SILENT

echo "====================="
echo "ADD GROUP WITH PICARD"
echo "====================="

$java -Xmx32G -jar $picard/AddOrReplaceReadGroups.jar \
I=${sample_id}.sort.fixmate.bam \
O=${sample_id}.sort.fixmate.group.bam \
SORT_ORDER=coordinate \
RGID=4 \
RGLB=lib1 \
RGPL=illumina \
RGPU=unit1 \
RGSM=20 \
CREATE_INDEX=true \
TMP_DIR="/home/student10/tmp"

echo "=============="
echo "FILTER BY GATK"
echo "=============="

$gatk PrintReads \
-I ${sample_id}.sort.fixmate.group.bam \
-O ${sample_id}.sort.fixmate.group.filter.bam \
--read-filter MappedReadFilter \
--read-filter PairedReadFilter \
--read-filter ProperlyPairedReadFilter

status=$?
echo "Status: $status" > test.txt