// :app - Krinik Tribit, the Compose app for Tribit Bluetooth speakers (MASTER_PLAN.md phase 2).
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "com.kriniks.tribit"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.kriniks.tribit"
        // [AI] Android 8: the app must install on the older phones Tribit owners use (GOAL.md, «для людей»).
        minSdk = 26
        targetSdk = 37
        versionCode = 1
        versionName = "0.1 (1)"
    }

    // Two builds (owner's rule R6, HOUSE_RULES.md): debug is «Debug Krinik Tribit» with the «Отладка» button in
    // Settings, release is «Krinik Tribit». The .debug suffix lets both stand side by side on one device. debug is
    // signed by the SDK's debug key, release by its own key from keystore.properties (outside git) - two keys.
    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            resValue("string", "app_name", "Debug Krinik Tribit")
        }
        release {
            resValue("string", "app_name", "Krinik Tribit")
        }
    }
    // The «Отладка» screen lives in src/debug; release gets the empty DebugTools of src/nodebug with the same API.
    sourceSets {
        getByName("release") { kotlin.directories.add("src/nodebug/kotlin") }
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
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.material3)
    testImplementation(libs.junit)
}
