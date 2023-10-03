#pragma once

#ifndef WORKSHOPID_HPP
#define WORKSHOPID_HPP

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

namespace WorkshopID
{
	void get_workshop_id_from_json();
}

#endif // WORKSHOPID_HPP
