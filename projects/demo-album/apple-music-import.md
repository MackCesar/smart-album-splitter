]# Importing to Apple Music (macOS / iOS)

## Best format
- **ALAC in `.m4a`** (Apple Lossless) is native for Apple Music. Set in `project.yml`:
  
- ```yaml
  output:
    codec: alac
  ```
  ### macOS Music app (local library)
	1.	Open Music (the macOS app).
	2.	Drag the output folder (e.g., projects/<slug>/output/) into Music or use:
	•	File → Import… and select all .m4a files.
	3.	Music reads tags from files:
	•	Album, Album Artist, Year, Genre, Comments, Track Number.
	•	Embedded cover appears automatically if present.
	4.	Optional: Create a playlist from the imported tracks:
	•	Select tracks → right click → Add to Playlist → New Playlist.

  ### iPhone / iPad (sync from Mac)
	•	If you use local sync (Finder → iPhone → Music), ensure those tracks/playlists are selected to sync.

  ### iCloud Music Library / Apple Music (streaming library)
	•	If you have Sync Library enabled (Music → Settings → General → Sync Library), imported files are matched/uploaded to your iCloud Music Library and should appear across devices. Upload/match can take a few minutes.

  ### **Artwork & tags**
	•	ALAC .m4a supports MP4/QuickTime tags. If artwork or a tag looks off:
	1.	In Music, select track(s) → Song Info → Artwork tab → add/replace image.
	2.	Or ensure the splitter embedded art (cover path or video snapshot) and re-import.

  ### Converting existing FLACs to ALAC

    If you split to FLAC but want Apple-native ALAC:

    ```bash
    for f in projects/<slug>/output/*.flac; do
      ffmpeg -y -i "$f" -c:a alac "${f%.flac}.m4a"
    done
    ```

Then import the .m4a files.