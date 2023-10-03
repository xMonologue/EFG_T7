#include <iostream>
#include <string>
#include <windows.h>
#include <thread>
#include <stdio.h>
#include <filesystem>
#include <curl/curl.h>
#include <zlib.h>
#include <zip.h>
#include "unzip.h"
#include <utils/io.hpp>
#include "steamcmd.hpp"
#include "std_include.hpp"
#include "command.hpp"
#include "component/steam_proxy.hpp"
#include <stdlib.h>
#include "component/party.hpp"
#include "loader/component_loader.hpp"
#include "game/game.hpp"
#include "steam/steam.hpp"
#include "network.hpp"
#include "workshop.hpp"
#include <utils/hook.hpp>
#include <utils/string.hpp>
#include <utils/info_string.hpp>
#include <version.hpp>
#include "game/utils.hpp"
#include <fstream>
#include <direct.h>
#include <limits.h>
#include <chrono>
#include <vector>

#include "steamcmd.hpp"
#include "workshopID.hpp"

namespace WorkshopID
{
	std::string get_current_path()
	{
		char buff[MAX_PATH];
		GetModuleFileName(NULL, buff, MAX_PATH);
		std::string::size_type position = std::string(buff).find_last_of("\\/");
		return std::string(buff).substr(0, position);
	}

	int write_pubid_to_file(std::string pubID)
	{
		const std::string& config_path = get_current_path() + "/zone/server_zm.cfg";

		std::vector<std::string> lines;
		bool line_exists = false;

		std::string line_to_find = "set workshop_id";
		std::string new_string = "set workshop_id \"" + pubID + "\"";

		FILE* inputFile;
		if (fopen_s(&inputFile, config_path.c_str(), "r") != 0)
		{
			printf("Error opening server_zm.cfg file.\n");
			return 1;
		}

		char buffer[1024];
		while (fgets(buffer, sizeof(buffer), inputFile))
		{
			std::string line(buffer);
			if (line.find(line_to_find) != std::string::npos)
			{
				printf("Line replaced with new workshop id in /zone/server_zm.cfg.\n");
				lines.push_back(new_string);
				line_exists = true;
			}
			else
			{
				lines.push_back(line);
			}
		}

		fclose(inputFile);

		if (!line_exists)
		{
			lines.push_back(new_string);
			printf("The 'workshop_id' dvar added in /zone/server_zm.cfg successfully.\n");
		}

		FILE* outputFile;
		if (fopen_s(&outputFile, config_path.c_str(), "w") != 0)
		{
			printf("Error opening or adding the workshop_id dvar to server_zm.cfg file.\n");
			return 1;
		}

		for (const std::string& updated_line : lines)
		{
			fprintf(outputFile, "%s", updated_line.c_str());
		}

		fclose(outputFile);

		return 0;
	}

    void read_json_for_id(std::filesystem::path path)
    {
        const auto json_str = utils::io::read_file(path);

        if (json_str.empty())
        {
            printf("[ WorkshopID ] workshop.json has not been found in folder \n");
            return;
        }

        rapidjson::Document doc;
        const rapidjson::ParseResult parse_result = doc.Parse(json_str);

        if (parse_result.IsError() || !doc.IsObject())
        {
            printf("[ WorkshopID ] Unable to parse workshop.json from folder \n");
            return;
        }

        if (!doc.HasMember("PublisherID"))
        {
            printf("[ WorkshopID ] PublisherID not found workshop.json is invalid \n");
            return;
        }

        std::string pubID = doc["PublisherID"].GetString();
		write_pubid_to_file(pubID);
    }

	void get_workshop_id_from_json()
	{
		const std::string& usermaps_path = get_current_path() + "/usermaps";
		std::string mapname = game::get_dvar_string("mapname");

		for (const auto& entry : std::filesystem::directory_iterator(usermaps_path))
		{
			if (entry.is_directory() && entry.path().filename() == mapname.data())
			{
				std::filesystem::path workshop_json;

				workshop_json = entry.path() / "workshop.json";
				if (std::filesystem::exists(workshop_json) && !std::filesystem::is_directory(workshop_json))
				{
					read_json_for_id(workshop_json);
					break;
				}

				workshop_json = entry.path() / "zone/workshop.json";
				if (std::filesystem::exists(workshop_json) && !std::filesystem::is_directory(workshop_json))
				{
					read_json_for_id(workshop_json);
					break;
				}
			}
		}
	}
}
