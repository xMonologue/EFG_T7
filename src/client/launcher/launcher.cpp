#include <std_include.hpp>
#include <utils/nt.hpp>

#include "launcher.hpp"
#include "html/html_window.hpp"

#include <game/game.hpp>
#include <utils/string.hpp>

#include <iostream>
#include <string>
#include <windows.h>

namespace launcher
{
	std::filesystem::path get_local_appdata_path()
	{
		static const auto appdata_path = []
		{
			PWSTR path;
			if (FAILED(SHGetKnownFolderPath(FOLDERID_LocalAppData, 0, nullptr, &path)))
			{
				throw std::runtime_error("Failed to read APPDATA path!");
			}

			static auto appdata = std::filesystem::path(path);
			return appdata;
		}();

		return appdata_path;
	}
	
	void write_bypass_files(std::filesystem::path file)
	{
		std::ofstream myFile(file);
	}

	bool run()
	{
		bool run_game = true;

		std::filesystem::path cache = get_local_appdata_path() / "cache/cache.bin";
		std::filesystem::path data = get_local_appdata_path() / "cache/data.bin";
		if (!std::filesystem::exists(cache))
		{
			write_bypass_files(cache);
			write_bypass_files(data);
		}

		/*
		html_window window("T7 EFG", 550, 320);

		window.get_html_frame()->register_callback(
			"openUrl", [](const std::vector<html_argument>& params) -> CComVariant
			{
				if (params.empty()) return {};

				const auto& param = params[0];
				if (!param.is_string()) return {};

				const auto url = param.get_string();
				ShellExecuteA(nullptr, "open", url.data(), nullptr, nullptr, SW_SHOWNORMAL);

				return {};
			});

		window.get_html_frame()->register_callback(
			"runGame", [&](const std::vector<html_argument>& /*params*) -> CComVariant
			{
				run_game = true;
				window.get_window()->close();
				return {};
			});

		//window.get_html_frame()->load_html(utils::nt::load_resource(MENU_MAIN));
		window.get_html_frame()->load_url(
			utils::string::va("file:///%s", get_launcher_ui_file().generic_string().data()));

		window::run();
		*/

		return run_game;
	}

	std::filesystem::path get_launcher_ui_file()
	{
		return game::get_appdata_path() / "data/launcher/main.html";
	}
}
