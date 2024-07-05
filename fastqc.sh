sample_id=$1
output_dir=$2

log_file="fastqc.log"
exec > >(tee -i $log_file)
exec 2>&1

if [ -f ${sample_id}_1.paired.fastq ] && [ -f ${sample_id}_2.paired.fastq ]; then
    fastqc ${sample_id}_1.paired.fastq ${sample_id}_2.paired.fastq -o ${output_dir}
else
    fastqc ${sample_id}_1.fastq.gz ${sample_id}_2.fastq.gz -o ${output_dir}
fi
