import spotipy
import spotipy.util as util
import pandas as pd
import requests


def authorize_user(CLIENT_ID, CLIENT_SECRET, refresh_token):
	token = get_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token)
	try:
		spotify = spotipy.Spotify(auth = token['access_token'])
		return spotify
	except:
		print('Issue with Client ID : {}'.format(CLIENT_ID))
		return

def get_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token):
	url = 'https://accounts.spotify.com/api/token'
	payload = {
		'grant_type':'refresh_token',
		'refresh_token':refresh_token
	}
	auth = (CLIENT_ID, CLIENT_SECRET)
	token = requests.post(url, data = payload, auth = auth).json()
	return token

def follow_playlist(spotify, playlist_owner_id, playlist_id):
	spotify.user_playlist_follow_playlist(playlist_owner_id, playlist_id)

def get_playlist_data(filepath):
	playlist_owner_id, playlist_id = [], []
	df = pd.read_csv(filepath)
	for row in df.values:
		row = row[0].split(':')
		playlist_owner_id.append(row[2])
		playlist_id.append(row[-1])
	return playlist_owner_id, playlist_id

def get_user_info(filepath):
	df = pd.read_csv(filepath)
	username = df['USERNAME']
	client_id = df['client ID']
	client_secret = df['client secret']
	refresh_token = df['oAUTH Access Refresh']
	return username, client_id, client_secret, refresh_token

if __name__ == '__main__':

	playlist_owner_ids, playlist_ids = get_playlist_data('SAMPLE DATA - PLAYLIST URI - Sheet1.csv')
	usernames, client_ids, client_secrets, refresh_tokens = get_user_info('SPOTIFY ACCOUNTS - Sheet1.csv')

	for user, c_id, c_secret, token in zip(usernames, client_ids, client_secrets, refresh_tokens):
		spotify = authorize_user(c_id, c_secret, token)
		if spotify is not None:
			for pl_owner_id, pl_id in zip(playlist_owner_ids, playlist_ids):
				follow_playlist(spotify, pl_owner_id, pl_id)


