// :app - Krinik Tribit, the Compose app for Tribit Bluetooth speakers (MASTER_PLAN.md phase 2).
import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "com.kriniks.tribit"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.kriniks.tribit"
        // Android 13 and up - the owner, 2026-10-16 ≈ 15:45 +03:00: «минимальная поддерживаемая версия от андроида 13 и
        // выше» (MASTER_PLAN.md journal). On 13+ the speaker search runs with BLUETOOTH_SCAN neverForLocation: no location.
        minSdk = 33
        targetSdk = 37
        versionCode = 1
        versionName = "0.1 (1)"
    }

    // Two builds (owner's rule R6, HOUSE_RULES.md): debug is «Debug Krinik Tribit» with the «Отладка» button in
    // Settings, release is «Krinik Tribit». The .debug suffix lets both stand side by side on one device. debug is
    // signed by the SDK's debug key, release by its own key from keystore.properties (outside git) - two keys.
    // The release key: keys/krinik-tribit-app-release.jks, its path and passwords in .env at the project root (KT_RELEASE_*),
    // all outside git - the owner, 2026-10-16 ≈ 17:27 +03:00: «ключ подписи релиз сборки в .env, вне гита» (HOUSE_RULES.md
    // R6: two keys, values never in chat, logs or commits). Without them the release build stays unsigned and still builds.
    val env = rootProject.file(".env").takeIf { it.exists() }?.let { f ->
        Properties().apply { f.inputStream().use { load(it) } }
    }
    val releaseKey = env?.getProperty("KT_RELEASE_STORE_FILE")?.takeIf { it.isNotBlank() }
    signingConfigs {
        if (env != null && releaseKey != null) create("release") {
            storeFile = rootProject.file(releaseKey)
            storePassword = env.getProperty("KT_RELEASE_STORE_PASSWORD")
            keyAlias = env.getProperty("KT_RELEASE_KEY_ALIAS")
            keyPassword = env.getProperty("KT_RELEASE_KEY_PASSWORD")
        }
    }

    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            resValue("string", "app_name", "Debug Krinik Tribit")
        }
        release {
            resValue("string", "app_name", "Krinik Tribit")
            // R8 and resource shrinking - always in release: the owner, 2026-10-16 ≈ 17:27 +03:00: «и релиз зборки обязатно в
            // R8» (HOUSE_RULES.md R6); speed as KARTUN (researches/11 §4a.2).
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
            if (releaseKey != null) signingConfig = signingConfigs.getByName("release")
        }
    }
    // The «Отладка» screen lives in src/debug; release gets the empty DebugTools of src/nodebug with the same API.
    sourceSets {
        getByName("release") { kotlin.directories.add("src/nodebug/kotlin") }
        // Tribit's speaker photos live in the PRIVATE repository native/ (KrinikTribitNative): the owner, 2026-10-16
        // ≈ 20:3x +03:00: «фото можно публиковать в мой приватный репозиторий» · «который мы делали по реверсу приложения
        // Трибит». With native/ beside the app the photo is built in; without it (a clone of the public storefront) a drawn
        // stand-in of the same name keeps the build working.
        val photos = rootProject.file("native/krinik-app/res")
        getByName("main") { res.directories.add(if (photos.isDirectory) photos.path else "src/photostub/res") }
    }
    buildFeatures {
        compose = true
        resValues = true
        buildConfig = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.material3)
    testImplementation(libs.junit)
    // org.json is part of Android; on the JVM its stub throws - the real library runs the settings-file tests (ProfileTest).
    testImplementation(libs.json)
}
