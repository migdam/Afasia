// ESLint for the web app's scripts (backlog P3-3a), run by scripts/check.sh.
// They are classic scripts that share globals, loaded in the order of
// frontend/index.html, so each one may use what the others define.
import js from "@eslint/js";
import globals from "globals";

const shared = {
    // i18n.js
    i18n: "readonly", translations: "readonly", LOCALES: "readonly", PLURAL_FORMS: "readonly",
    // api.js
    api: "readonly", API_BASE_URL: "readonly",
    // chart.js
    SimpleChart: "readonly",
    // audio.js
    audioRecorder: "readonly", audioPlayer: "readonly", speechRecognizer: "readonly", reader: "readonly",
    // ui.js
    ui: "readonly", el: "readonly", translated: "readonly", showEmpty: "readonly",
    EXERCISE_TYPE_KEYS: "readonly", BADGE_KEYS: "readonly",
};

export default [
    js.configs.recommended,
    {
        files: ["frontend/**/*.js"],
        languageOptions: {
            ecmaVersion: 2022,
            sourceType: "script",
            globals: { ...globals.browser, ...shared },
        },
        rules: {
            // A script's top-level names are for the other scripts.
            "no-unused-vars": ["error", { vars: "local" }],
            "no-redeclare": ["error", { builtinGlobals: false }],
        },
    },
    {
        files: ["frontend/sw.js"],
        languageOptions: { globals: globals.serviceworker },
    },
];
