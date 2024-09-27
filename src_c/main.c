#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "cJSON.h"


enum file_type
{
    GRP,
    JSON,
    UNKNOWN
};

typedef struct
{
    uint32_t parts_name_hash; // 0
    uint32_t parts_id;        // 4
    uint32_t submesh_count;         // 8 - This may be the number of submeshes
    uint32_t count_T;         // C
    uint32_t count_s;         // 0x10
    uint32_t mesh_count;     // 0x14 - This may be the number of meshes
    uint32_t count_set_T;     // 0x18
    uint32_t count_set_s;     // 0x1C

} GRPEntry;
const size_t ENTRY_SIZE = sizeof(GRPEntry); //0x20

typedef struct
{
    size_t file_size;
    size_t num_entries;
    GRPEntry *entries;
} GRPfile;

void init_grp_entry(GRPEntry *entry)
{
    entry->parts_name_hash = 0x3057221F; // "default"
    entry->parts_id = 0;
    entry->submesh_count = entry->count_T = entry->count_s = 0;
    entry->mesh_count = entry->count_set_T = entry->count_set_s = 0;
}

enum file_type get_file_type(const char *filename)
{
    char *ext = strrchr(filename, '.');
    enum file_type filetype = UNKNOWN;
    if (ext == NULL)
    {
        filetype = UNKNOWN; // redundant
    }
    else if (strcmp(ext, ".grp") == 0 || strcmp(ext, ".GRP") == 0)
    {
        filetype = GRP;
    }
    else if (strcmp(ext, ".json") == 0 || strcmp(ext, ".JSON") == 0)
    {
        filetype = JSON;
    }
    // free(ext);
    return filetype;
}

int grp_to_json(char* filename) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL)        {
        fprintf(stderr, "ERROR: Could not open file: %s\n", filename);
        return 1;
    }
    GRPfile grp;

    fseek(file, 0, SEEK_END);
    grp.file_size = ftell(file);
    if (grp.file_size % ENTRY_SIZE != 0)        {
        fprintf(stderr, "ERROR: Invalid file size: %s,  %d mod %d != 0 \n", filename, grp.file_size, ENTRY_SIZE);
        fclose(file);
        return 1;
    }
    fseek(file, 0, SEEK_SET);
    grp.num_entries = grp.file_size / ENTRY_SIZE;

    grp.entries = (GRPEntry *)malloc(grp.num_entries * ENTRY_SIZE);
    if (grp.entries == NULL)        {
        fprintf(stderr, "ERROR: unable to allocate memory for %d entries\n", grp.num_entries);
        fclose(file);
        return 1;
    }
    for (size_t i = 0; i < grp.num_entries; i++) {
        init_grp_entry(&grp.entries[i]);
    }
    fread(grp.entries, sizeof(GRPEntry), grp.num_entries, file);
    fclose(file);
    //save to json
    size_t length = strlen(filename);
    char* json_filename = (char *)malloc(length + 1);
    strncpy(json_filename, filename, length - 4);
    strcpy(json_filename + length - 4, ".json");

    cJSON *json = cJSON_CreateObject();
    cJSON *entries_array = cJSON_CreateArray();
    for (size_t i = 0; i < grp.num_entries; i++) {
        GRPEntry *entry = &grp.entries[i];
        cJSON *entry_json = cJSON_CreateObject();

        char hex_str[9];
        sprintf(hex_str, "%08X", entry->parts_name_hash);
        cJSON_AddStringToObject(entry_json, "parts_name_hash", hex_str);
        sprintf(hex_str, "%08X", entry->parts_id);
        cJSON_AddStringToObject(entry_json, "parts_id", hex_str);
        cJSON_AddNumberToObject(entry_json, "submesh_count", entry->submesh_count);
        cJSON_AddNumberToObject(entry_json, "count_T", entry->count_T);
        cJSON_AddNumberToObject(entry_json, "count_s", entry->count_s);
        cJSON_AddNumberToObject(entry_json, "mesh_count", entry->mesh_count);
        cJSON_AddNumberToObject(entry_json, "count_set_T", entry->count_set_T);
        cJSON_AddNumberToObject(entry_json, "count_set_s", entry->count_set_s);

        cJSON_AddItemToArray(entries_array, entry_json);
    }
    cJSON_AddStringToObject(json, "file_type", "GRP");
    cJSON_AddNumberToObject(json, "entries_count_reference_only", grp.num_entries);
    cJSON_AddItemToObject(json, "entries", entries_array);
    char *json_string = cJSON_Print(json);

    FILE *json_file = fopen(json_filename, "w");
    int result = 0;
    if (json_file == NULL) {
        fprintf(stderr, "ERROR: Could not open file: %s\n", json_filename);
        result = 1;
    } else {
        fprintf(json_file, "%s", json_string);
        fclose(json_file);
    }

    cJSON_Delete(json);
    free(json_string);
    // free(filename);
    free(json_filename);
    free(grp.entries);
    return result;
}

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Usage: %s <file>\n", argv[0]);
        return 1;
    }
    printf("Converting %s\n", argv[1]);
    char *filename = argv[1];
    enum file_type filetype = get_file_type(filename);
    if (filetype == GRP) {
        printf("Converting %s to JSON\n", filename);
        return grp_to_json(filename);
    } else if (filetype == JSON) {
        printf("Converting %s to GRP\n", filename);
        //json_to_grp(filename);
        return 1;
    } else if (filetype == UNKNOWN) {
        fprintf(stderr, "ERROR: Unknown file type: %s\n", filename);
        return 1;
    }
    printf("Done\n");

    return 0; //redundant
}