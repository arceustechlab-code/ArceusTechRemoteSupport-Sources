"""Publish only verified Windows user-session client packages after the build succeeds."""
import publish_clients as publisher

publisher.RUN = 37115254879
publisher.EXPECTED_HEAD_SHA = '2fb14423c0af98444380ddb54615e17edd9c958d'
publisher.PATCH_REVISION = '2fb14423c0af98444380ddb54615e17edd9c958d'
publisher.PLATFORMS = {'windows-x64': ('ArceusTechRemoteSupport', ['-Setup.exe', '-Windows-x64.zip'], '-Windows-x64-source.tar.gz')}
publisher.ASSET_PLATFORM_ALIASES['windows-x64'] = 'windows-x64-licensefix'
publisher.TAG = 'v2026.10.03-windows-user-beta'
publisher.main()
