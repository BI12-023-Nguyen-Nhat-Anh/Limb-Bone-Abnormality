java="java"
TOOLS_PATH="/home/student10"
picard="$TOOLS_PATH/picard-tools-1.119"
gatk="$TOOLS_PATH/gatk/gatk-4.1.2.0/gatk"
G_REF="/storage/student10/hg38.fa"
sample_id=$1

echo "==========================="
echo "REMOVE DUPLICATES BY Picard"
echo "==========================="

#$java -Xmx32G -jar $picard/MarkDuplicates.jar \
$java -Xmx20G -jar $picard/MarkDuplicates.jar \
I=${sample_id}.sort.fixmate.group.filter.bam \
O=${sample_id}.sort.fixmate.group.filter.markdup.bam \
M=${sample_id}_marked_dup_metric.txt \
CREATE_INDEX=true \
TMP_DIR="/home/student10/tmp" \
VALIDATION_STRINGENCY=SILENT 
#Note: markdup = marked duplicates

echo "=================================="
echo "FILTER LOW QUALTIY MAPPING BY GATK"
echo "=================================="

#$java -Xmx32G -jar $gatk \
$gatk PrintReads \
-I ${sample_id}.sort.fixmate.group.filter.markdup.bam \
-O ${sample_id}.sort.fixmate.group.filter.markdup.FLQM.bam \
--read-filter MappingQualityReadFilter \
--minimum-mapping-quality 10 
#Note: FLQM = Filter low quality mapping

echo "=========================================="
echo "CALLING VARIANT BY HAPLOTYPECALLER IN GATK"
echo "=========================================="
#$java -Xmx32G -jar $gatk
$gatk HaplotypeCaller -R $G_REF -I ${sample_id}.sort.fixmate.group.filter.markdup.FLQM.bam \
-O ${sample_id}.raw.vcf

#################################################
#SEPARATE RAW VCF INTO SNPS AND INDELS VCF FILES#
#################################################

echo "========================================================"
echo "SEPERATE RAW DATA INTO SNPS AND INDELS FILES BY VCFTOOLS"
echo "========================================================"

vcftools --vcf ${sample_id}.raw.vcf --out ${sample_id}.indels.raw \
--keep-only-indels --recode --recode-INFO-all

vcftools --vcf ${sample_id}.raw.vcf --out ${sample_id}.SNPs.raw \
--remove-indels --recode --recode-INFO-all

#index snps and indels raw files

#$java -Xmx32G -jar
$gatk IndexFeatureFile --feature-file ${sample_id}.SNPs.raw.recode.vcf
#$java -Xmx32G -jar
$gatk IndexFeatureFile --feature-file ${sample_id}.indels.raw.recode.vcf 

echo "=========================="
echo "VARIANT FILTRATION BY GATK"
echo "=========================="

#$java -Xmx32G -jar
$gatk VariantFiltration \
--output  ${sample_id}.indels.vcf \
--variant ${sample_id}.indels.raw.recode.vcf \
-R $G_REF \
--filter-expression "QD < 2.0" \
--filter-name "QDFilter" \
--filter-expression "ReadPosRankSum < -20.0" \
--filter-name "ReadPosFilter" \
--filter-expression "FS > 200.0" \
--filter-name "FSFilter" \
--filter-expression "MQ0 >= 4 && ((MQ0 / (1.0*DP)) > 0.1)" \
--filter-name "HARD_TO_VALIDATE" \
--filter-expression "QUAL < 30.0 || DP < 6 || DP > 5000 || HRun > 5" \
--filter-name "QualFilter"

mline2=`grep -n "#CHROM" ${sample_id}.indels.vcf | cut -d':' -f 1`
head -n $mline2 ${sample_id}.indels.vcf > ${sample_id}.headindels.vcf
cat ${sample_id}.indels.vcf | grep PASS \
  | cat ${sample_id}.headindels.vcf -> ${sample_id}.indels.PASS.vcf

#index indels pass files

#$java -Xmx32G -jar
$gatk IndexFeatureFile --feature-file ${sample_id}.indels.PASS.vcf

#variant filtration snps file

#$java -Xmx32G -jar
$gatk VariantFiltration \
-R $G_REF \
--output ${sample_id}.SNPs.vcf \
--variant ${sample_id}.SNPs.raw.recode.vcf \
--mask ${sample_id}.indels.PASS.vcf \
--mask-name InDel \
--cluster-size 3 \
--cluster-window-size 10 \
--filter-expression "QD < 2.0" \
--filter-name "QDFilter" \
--filter-expression "MQ < 40.0" \
--filter-name "MQFilter" \
--filter-expression "FS > 60.0" \
--filter-name "FSFilter" \
--filter-expression "HaplotypeScore > 13.0" \
--filter-name "HaplotypeScoreFilter" \
--filter-expression "MQRankSum < -12.5" \
--filter-name "MQRankSumFilter" \
--filter-expression "ReadPosRankSum < -8.0" \
--filter-name "ReadPosRankSumFilter" \
--filter-expression "QUAL < 30.0 || DP < 6 || DP > 5000 ||HRun > 5" \
--filter-name "StandardFilters" \
--filter-expression "MQ0 >= 4 && ((MQ0 / (1.0 * DP)) > 0.1)" \
--filter-name "HARD_TO_VALIDATE"

mline=`grep -n "#CHROM" ${sample_id}.SNPs.vcf | cut -d':' -f 1`
head -n $mline ${sample_id}.SNPs.vcf > ${sample_id}.headSNPs.vcf
cat ${sample_id}.SNPs.vcf | grep PASS \
  | cat ${sample_id}.headSNPs.vcf -> ${sample_id}.SNPs.PASS.vcf

status=$?
echo "Status: $status" > test.txt