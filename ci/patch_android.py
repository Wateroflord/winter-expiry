"""Дописывает в Android-проект (созданный `flutter create`) всё, что нужно приложению:
разрешения, приёмники уведомлений, desugaring, название и версию Kotlin."""
import pathlib
import re
import sys

root = pathlib.Path("android")


def fail(msg):
    print("PATCH ERROR:", msg)
    sys.exit(1)


# ---------- AndroidManifest.xml ----------
manifest = root / "app/src/main/AndroidManifest.xml"
m = manifest.read_text(encoding="utf-8")

perms = """
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.VIBRATE"/>
"""
if "android.permission.CAMERA" not in m:
    m, n = re.subn(r"(<manifest[^>]*>)", r"\1" + perms, m, count=1)
    if n != 1:
        fail("manifest tag not found")

receivers = """
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
            </intent-filter>
        </receiver>
    </application>"""
if "ScheduledNotificationReceiver" not in m:
    if "</application>" not in m:
        fail("</application> not found")
    m = m.replace("</application>", receivers.lstrip("\n"), 1)

m = re.sub(r'android:label="[^"]*"', 'android:label="Просрочка"', m, count=1)
manifest.write_text(m, encoding="utf-8")

# ---------- app/build.gradle(.kts): desugaring для уведомлений ----------
kts = root / "app/build.gradle.kts"
groovy = root / "app/build.gradle"
if kts.exists():
    g = kts.read_text(encoding="utf-8")
    if "isCoreLibraryDesugaringEnabled" not in g:
        g, n = re.subn(r"compileOptions\s*\{", "compileOptions {\n        isCoreLibraryDesugaringEnabled = true", g, count=1)
        if n != 1:
            fail("compileOptions not found in build.gradle.kts")
        g += '\ndependencies {\n    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")\n}\n'
    kts.write_text(g, encoding="utf-8")
elif groovy.exists():
    g = groovy.read_text(encoding="utf-8")
    if "coreLibraryDesugaringEnabled" not in g:
        g, n = re.subn(r"compileOptions\s*\{", "compileOptions {\n        coreLibraryDesugaringEnabled true", g, count=1)
        if n != 1:
            fail("compileOptions not found in build.gradle")
        g += "\ndependencies {\n    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'\n}\n"
    groovy.write_text(g, encoding="utf-8")
else:
    fail("app build.gradle not found")

# ---------- compileSdk 36 (нужно сканеру) ----------
for gp in (kts, groovy):
    if gp.exists():
        t = gp.read_text(encoding="utf-8")
        t = re.sub(r"compileSdk\s*=\s*flutter\.compileSdkVersion", "compileSdk = 36", t)
        t = re.sub(r"compileSdkVersion\s+flutter\.compileSdkVersion", "compileSdkVersion 36", t)
        t = re.sub(r"minSdk\s*=\s*flutter\.minSdkVersion", "minSdk = 23", t)
        t = re.sub(r"minSdkVersion\s+flutter\.minSdkVersion", "minSdkVersion 23", t)
        gp.write_text(t, encoding="utf-8")

# ---------- settings.gradle(.kts): Kotlin поновее (нужно сканеру) ----------
for name in ("settings.gradle.kts", "settings.gradle"):
    s_path = root / name
    if s_path.exists():
        s = s_path.read_text(encoding="utf-8")
        s = re.sub(
            r'(id\s*\(?\s*["\']org\.jetbrains\.kotlin\.android["\']\s*\)?\s*version\s*)["\'](1\.[0-8][0-9.]*)["\']',
            r'\g<1>"2.1.0"',
            s,
        )
        s_path.write_text(s, encoding="utf-8")

# ---------- AGP 8.7.3 + Gradle 8.10.2 (нужно камере CameraX) ----------
for name in ("settings.gradle.kts", "settings.gradle"):
    s_path = root / name
    if s_path.exists():
        s = s_path.read_text(encoding="utf-8")
        s = re.sub(
            r'(id\s*\(?\s*["\']com\.android\.application["\']\s*\)?\s*version\s*)["\'][0-9.]+["\']',
            r'\g<1>"8.7.3"',
            s,
        )
        s_path.write_text(s, encoding="utf-8")
wrapper = root / "gradle/wrapper/gradle-wrapper.properties"
if wrapper.exists():
    w = wrapper.read_text(encoding="utf-8")
    w = re.sub(r"gradle-[0-9.]+-(all|bin)\.zip", "gradle-8.10.2-all.zip", w)
    wrapper.write_text(w, encoding="utf-8")
else:
    fail("gradle-wrapper.properties not found")

print("Android project patched OK")
