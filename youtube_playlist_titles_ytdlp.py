"""
YouTube Playlist Video Titles Extractor (using yt-dlp)

This script extracts and prints all video titles from a YouTube playlist.
Requires: yt-dlp library (pip install yt-dlp)

Usage: python youtube_playlist_titles_ytdlp.py
"""

import yt_dlp

def get_playlist_titles(playlist_url):
    """
    Extract and print all video titles from a YouTube playlist using yt-dlp.

    Args:
        playlist_url (str): The URL of the YouTube playlist
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Don't download, just extract metadata
        'force_generic_extractor': False,
    }

    try:
        print(f"Loading playlist: {playlist_url}\n")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract playlist info
            playlist_info = ydl.extract_info(playlist_url, download=False)

            # Print playlist details
            playlist_title = playlist_info.get('title', 'Unknown Playlist')
            entries = playlist_info.get('entries', [])

            print(f"Playlist: {playlist_title}")
            print(f"Number of videos: {len(entries)}\n")
            print("=" * 80)

            # Print video titles
            for idx, entry in enumerate(entries, start=1):
                title = entry.get('title', 'Unknown Title')
                print(f"{idx}. {title}")

            print("=" * 80)
            print(f"\nTotal videos: {len(entries)}")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have yt-dlp installed: pip install yt-dlp")

if __name__ == "__main__":
    # Get playlist URL from user
    playlist_url = input("Enter YouTube playlist URL: ").strip()

    if not playlist_url:
        print("Error: No URL provided")
        print("\nExample URL format:")
        print("https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxx")
    else:
        get_playlist_titles(playlist_url)

