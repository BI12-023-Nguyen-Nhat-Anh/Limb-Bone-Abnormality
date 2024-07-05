TOOLS_PATH="/home/student10"
trimmomatic="$TOOLS_PATH/miniconda3/envs/student10/bin/trimmomatic"
adapter="$TOOLS_PATH/TruSeq3-PE.fa"
sample_id=$1

trimmomatic PE \
-threads 10 -phred33 -trimlog ${sample_id}.log \
-summary ${sample_id}.log \
 ${sample_id}_1.fastq.gz ${sample_id}_2.fastq.gz \
${sample_id}_1.paired.fastq ${sample_id}_1.unpaired.fastq.gz \
${sample_id}_2.paired.fastq ${sample_id}_2.unpaired.fastq.gz \
ILLUMINACLIP:$adapter:2:30:10 \
LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36
read1=${sample_id}_1.paired.fastq
read2=${sample_id}_2.paired.fastq