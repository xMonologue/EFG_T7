#pragma once

#ifndef STEAMCMD_HPP
#define STEAMCMD_HPP

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
#include "party.hpp"

namespace steamcmd
{
	int start_new_process(const char* exePath, bool Hide_Window, bool waittill_done, const char* arguments);
	int extract_steamcmd();
	size_t write_data(void* ptr, size_t size, size_t nmemb, FILE* stream);
	int setup_steamcmd();
	void moveFolder(const std::string& sourceFolderPath, const std::string& destinationFolderPath);
	void initialize_download(std::string workshop_id, std::string modtype);
}

#endif // STEAMCMD_HPP
