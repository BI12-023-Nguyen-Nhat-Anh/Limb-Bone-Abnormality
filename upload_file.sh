HOST="http://dashboard.ulake.usth.edu.vn/api/file"

if [[ $1 != "" && $2 != "" ]]; then
    AUTH=$1
    NAME=$2
    OwnerId=$3
    folder_id=$4
    folder_name=$5
    # file_dir=$6
fi

# In ra giá trị của các biến để kiểm tra
echo "AUTH=$AUTH"
echo "NAME=$NAME"
echo "OwnerId=$OwnerId"
echo "folder_id=$folder_id"
echo "folder_name=$folder_name"
# echo "file_dir=$file_dir"

curl -v -X 'POST' \
    "$HOST" \
    -H "Authorization: Bearer $AUTH" \
    -H 'Content-Type: multipart/form-data' \
    -F "fileInfo={\"mime\": \"application/x-gzip\", \"name\": \"$NAME\", \"ownerId\": $OwnerId, \"parent\": { \"id\": $folder_id, \"ownerId\": $OwnerId, \"name\": \"$folder_name\"}};type=application/json" \
    -F "file=./"