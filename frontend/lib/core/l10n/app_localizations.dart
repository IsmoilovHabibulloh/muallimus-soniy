import 'package:flutter/material.dart';
import 'l10n_uz.dart';
import 'l10n_uz_cyrl.dart';
import 'l10n_ru.dart';
import 'l10n_en.dart';
import 'l10n_ar.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  late final Map<String, String> _strings = _loadStrings();

  Map<String, String> _loadStrings() {
    if (locale.languageCode == 'uz' && locale.countryCode == 'Cyrl') {
      return uzCyrlStrings;
    }
    switch (locale.languageCode) {
      case 'ru':
        return ruStrings;
      case 'en':
        return enStrings;
      case 'ar':
        return arStrings;
      default:
        return uzStrings;
    }
  }

  String _get(String key) => _strings[key] ?? uzStrings[key] ?? key;

  // ═══ Splash ═══
  String get welcome => _get('welcome');
  String get welcomeDescription => _get('welcomeDescription');
  String get wuduReminder => _get('wuduReminder');
  String get offlineNote => _get('offlineNote');
  String get continueButton => _get('continueButton');

  // ═══ Home ═══
  String get author => _get('author');
  String get secondTeacher => _get('secondTeacher');
  String pages(int count) => _get('pages').replaceAll('{count}', '$count');
  String get recitedBy => _get('recitedBy');
  String get authorLabel => _get('authorLabel');
  String get recitedByLabel => _get('recitedByLabel');
  String get foreword => _get('foreword');
  String get forewordBody => _get('forewordBody');
  String get startReading => _get('startReading');
  String get feedback => _get('feedback');
  String get lastReadPage => _get('lastReadPage');
  String pageN(int n) => _get('pageN').replaceAll('{n}', '$n');
  String get continueReading => _get('continueReading');

  // ═══ Settings ═══
  String get settings => _get('settings');
  String get theme => _get('theme');
  String get light => _get('light');
  String get dark => _get('dark');
  String get system => _get('system');
  String get language => _get('language');
  String get aboutApp => _get('aboutApp');
  String get privacyPolicy => _get('privacyPolicy');
  String get termsOfUse => _get('termsOfUse');
  String get about => _get('about');

  // ═══ Feedback ═══
  String get feedbackTitle => _get('feedbackTitle');
  String get feedbackSubtitle => _get('feedbackSubtitle');
  String get fillAllFields => _get('fillAllFields');
  String get yourName => _get('yourName');
  String get nameRequired => _get('nameRequired');
  String get phoneNumber => _get('phoneNumber');
  String get phoneRequired => _get('phoneRequired');
  String get phoneInvalid => _get('phoneInvalid');
  String get type => _get('type');
  String get suggestion => _get('suggestion');
  String get bugReport => _get('bugReport');
  String get details => _get('details');
  String get minChars => _get('minChars');
  String get submit => _get('submit');
  String get thanks => _get('thanks');
  String get feedbackSent => _get('feedbackSent');
  String get backToHome => _get('backToHome');
  String get errorOccurred => _get('errorOccurred');

  // ═══ TOC ═══
  String get tableOfContents => _get('tableOfContents');
  String get noToc => _get('noToc');
  String get retry => _get('retry');

  // ═══ Reader ═══
  String pageOf(int current, int total) =>
      _get('pageOf').replaceAll('{current}', '$current').replaceAll('{total}', '$total');
  String get pageNotFound => _get('pageNotFound');
  String get imageLoadFailed => _get('imageLoadFailed');
  String get error => _get('error');

  // ═══ Copyright ═══
  String get muslimBoardUz => _get('muslimBoardUz');
  String get allRightsReserved => _get('allRightsReserved');

  // ═══ Legal — Privacy ═══
  String get privacyTitle => _get('privacyTitle');
  String get privacyEffectiveDate => _get('privacyEffectiveDate');
  String get privacyIntroTitle => _get('privacyIntroTitle');
  String get privacyIntro1 => _get('privacyIntro1');
  String get privacyIntro2 => _get('privacyIntro2');
  String get privacyDataTitle => _get('privacyDataTitle');
  String get privacyVoluntary => _get('privacyVoluntary');
  String get privacyVoluntaryDesc => _get('privacyVoluntaryDesc');
  String get privacyDataType => _get('privacyDataType');
  String get privacyDataPurpose => _get('privacyDataPurpose');
  String get privacyDataName => _get('privacyDataName');
  String get privacyDataNamePurpose => _get('privacyDataNamePurpose');
  String get privacyDataPhone => _get('privacyDataPhone');
  String get privacyDataPhonePurpose => _get('privacyDataPhonePurpose');
  String get privacyDataFeedback => _get('privacyDataFeedback');
  String get privacyDataFeedbackPurpose => _get('privacyDataFeedbackPurpose');
  String get privacyImportantNote => _get('privacyImportantNote');
  String get privacyLocalStorage => _get('privacyLocalStorage');
  String get privacyLocalStorageDesc => _get('privacyLocalStorageDesc');
  String get privacyLocalItem1 => _get('privacyLocalItem1');
  String get privacyLocalItem2 => _get('privacyLocalItem2');
  String get privacyLocalItem3 => _get('privacyLocalItem3');
  String get privacyNotCollected => _get('privacyNotCollected');
  String get privacyNotGps => _get('privacyNotGps');
  String get privacyNotContacts => _get('privacyNotContacts');
  String get privacyNotDevice => _get('privacyNotDevice');
  String get privacyNotAds => _get('privacyNotAds');
  String get privacyNotFinance => _get('privacyNotFinance');
  String get privacyNotBiometric => _get('privacyNotBiometric');
  String get privacyUsageTitle => _get('privacyUsageTitle');
  String get privacyUsageDesc => _get('privacyUsageDesc');
  String get privacyUsage1 => _get('privacyUsage1');
  String get privacyUsage2 => _get('privacyUsage2');
  String get privacyUsage3 => _get('privacyUsage3');
  String get privacyUsageNoMarketing => _get('privacyUsageNoMarketing');
  String get privacyThirdPartyTitle => _get('privacyThirdPartyTitle');
  String get privacyThirdParty1 => _get('privacyThirdParty1');
  String get privacyThirdParty2 => _get('privacyThirdParty2');
  String get privacySecurityTitle => _get('privacySecurityTitle');
  String get privacySecurity1 => _get('privacySecurity1');
  String get privacySecurity2 => _get('privacySecurity2');
  String get privacySecurity3 => _get('privacySecurity3');
  String get privacySecurity4 => _get('privacySecurity4');
  String get privacyRightsTitle => _get('privacyRightsTitle');
  String get privacyRight1 => _get('privacyRight1');
  String get privacyRight2 => _get('privacyRight2');
  String get privacyRight3 => _get('privacyRight3');
  String get privacyRight4 => _get('privacyRight4');
  String get privacyRightsContact => _get('privacyRightsContact');
  String get privacyChildrenTitle => _get('privacyChildrenTitle');
  String get privacyChildrenDesc => _get('privacyChildrenDesc');
  String get privacyThirdServicesTitle => _get('privacyThirdServicesTitle');
  String get privacyThirdServicesDesc => _get('privacyThirdServicesDesc');
  String get privacyLawTitle => _get('privacyLawTitle');
  String get privacyLaw1 => _get('privacyLaw1');
  String get privacyLaw2 => _get('privacyLaw2');
  String get privacyLaw3 => _get('privacyLaw3');
  String get privacyLaw4 => _get('privacyLaw4');
  String get privacyContactTitle => _get('privacyContactTitle');
  String get contactCompany => _get('contactCompany');
  String get contactEmail => _get('contactEmail');
  String get contactApp => _get('contactApp');
  String get privacyFooter => _get('privacyFooter');

  // ═══ Legal — Terms ═══
  String get termsTitle => _get('termsTitle');
  String get termsEffectiveDate => _get('termsEffectiveDate');
  String get termsGeneralTitle => _get('termsGeneralTitle');
  String get termsGeneral1 => _get('termsGeneral1');
  String get termsGeneral2 => _get('termsGeneral2');
  String get termsDescTitle => _get('termsDescTitle');
  String get termsDesc => _get('termsDesc');
  String get termsLegalBasis => _get('termsLegalBasis');
  String get termsRightsTitle => _get('termsRightsTitle');
  String get termsRight1 => _get('termsRight1');
  String get termsRight2 => _get('termsRight2');
  String get termsRight3 => _get('termsRight3');
  String get termsProhibitedTitle => _get('termsProhibitedTitle');
  String get termsProhibited1 => _get('termsProhibited1');
  String get termsProhibited2 => _get('termsProhibited2');
  String get termsProhibited3 => _get('termsProhibited3');
  String get termsProhibited4 => _get('termsProhibited4');
  String get termsProhibited5 => _get('termsProhibited5');
  String get termsLicenseTitle => _get('termsLicenseTitle');
  String get termsLicenseDesc => _get('termsLicenseDesc');
  String get termsLicense1 => _get('termsLicense1');
  String get termsLicense2 => _get('termsLicense2');
  String get termsLicense3 => _get('termsLicense3');
  String get termsLicense4 => _get('termsLicense4');
  String get termsLiabilityTitle => _get('termsLiabilityTitle');
  String get termsLiabilityDesc => _get('termsLiabilityDesc');
  String get termsInternetTitle => _get('termsInternetTitle');
  String get termsInternetDesc => _get('termsInternetDesc');
  String get termsInternet1 => _get('termsInternet1');
  String get termsInternet2 => _get('termsInternet2');
  String get termsInternet3 => _get('termsInternet3');
  String get termsIPTitle => _get('termsIPTitle');
  String get termsIP1 => _get('termsIP1');
  String get termsIP2 => _get('termsIP2');
  String get termsDisputeTitle => _get('termsDisputeTitle');
  String get termsDisputeDesc => _get('termsDisputeDesc');
  String get termsContactTitle => _get('termsContactTitle');
  String get termsFooter => _get('termsFooter');

  // ═══ Legal — About ═══
  String get aboutTitle => _get('aboutTitle');
  String get aboutSubtitle => _get('aboutSubtitle');
  String get aboutAppName => _get('aboutAppName');
  String get aboutVersion => _get('aboutVersion');
  String get aboutDeveloper => _get('aboutDeveloper');
  String get aboutCategory => _get('aboutCategory');
  String get aboutCategoryValue => _get('aboutCategoryValue');
  String get aboutPrice => _get('aboutPrice');
  String get aboutPriceValue => _get('aboutPriceValue');
  String get aboutLicense => _get('aboutLicense');
  String get aboutDescTitle => _get('aboutDescTitle');
  String get aboutDesc => _get('aboutDesc');
  String get aboutLegalBasis => _get('aboutLegalBasis');
  String get aboutAuthorTitle => _get('aboutAuthorTitle');
  String get aboutAuthorDesc => _get('aboutAuthorDesc');
  String get aboutAudioTitle => _get('aboutAudioTitle');
  String get aboutAudioDesc => _get('aboutAudioDesc');
  String get aboutFeaturesTitle => _get('aboutFeaturesTitle');
  String get aboutFeature1 => _get('aboutFeature1');
  String get aboutFeature2 => _get('aboutFeature2');
  String get aboutFeature3 => _get('aboutFeature3');
  String get aboutFeature4 => _get('aboutFeature4');
  String get aboutFeature5 => _get('aboutFeature5');
  String get aboutFeature6 => _get('aboutFeature6');
  String get aboutFeature7 => _get('aboutFeature7');
  String get aboutTechTitle => _get('aboutTechTitle');
  String get aboutOpenSourceTitle => _get('aboutOpenSourceTitle');
  String get aboutOpenSource1 => _get('aboutOpenSource1');
  String get aboutOpenSource2 => _get('aboutOpenSource2');
  String get aboutPublishTitle => _get('aboutPublishTitle');
  String get aboutOriginalAuthor => _get('aboutOriginalAuthor');
  String get aboutPublishBasis => _get('aboutPublishBasis');
  String get aboutAudio => _get('aboutAudio');
  String get aboutDigitization => _get('aboutDigitization');
  String get aboutPublishYear => _get('aboutPublishYear');
  String get aboutThanksTitle => _get('aboutThanksTitle');
  String get aboutThanks1 => _get('aboutThanks1');
  String get aboutThanks2 => _get('aboutThanks2');
  String get aboutThanks3 => _get('aboutThanks3');
  String get aboutThanks4 => _get('aboutThanks4');
  String get aboutThanks5 => _get('aboutThanks5');
  String get aboutContactTitle => _get('aboutContactTitle');
  String get aboutFooter => _get('aboutFooter');
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    if (locale.languageCode == 'uz') return true;
    return ['en', 'ru', 'ar'].contains(locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
