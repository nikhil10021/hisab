export const UI_TEXT = {
  brand: {
    name: 'Hisab',
    tagline: 'Clear tools for everyday money decisions.',
  },
  navigation: {
    home: 'Home',
    about: 'About',
    methodology: 'Methodology',
    terms: 'Terms',
    privacy: 'Privacy',
    primaryNavigation: 'Primary navigation',
    footerNavigation: 'Footer navigation',
    searchLabel: 'Search calculators',
    searchPlaceholder: 'Search calculators',
  },
  home: {
    eyebrow: 'Personal finance, made clear',
    title: 'Make your next money decision with confidence.',
    description:
      'Explore clear, straightforward tools for everyday financial decisions.',
    calculatorListTitle: 'Calculators',
    emptyTitle: 'No calculators available yet',
    emptyMessage: 'Please check back soon for available calculators.',
    noSearchResultsTitle: 'No matching calculators',
    noSearchResultsMessage: 'Try a different search term.',
  },
  calculator: {
    title: 'Calculator',
    placeholder:
      'This calculator page is being prepared. Calculator inputs and results will be provided by the backend.',
  },
  category: {
    title: 'Category',
    placeholder: 'Category details will be available here.',
  },
  pages: {
    about: {
      title: 'About Hisab',
      description: 'Simple finance calculators for everyday decisions.',
    },
    methodology: {
      title: 'Methodology',
      description:
        'Calculator methods and assumptions will be documented here.',
    },
    terms: {
      title: 'Terms',
      description: 'Terms information will be available here.',
    },
    privacy: {
      title: 'Privacy',
      description: 'Privacy information will be available here.',
    },
  },
  errors: {
    pageNotFoundTitle: 'Page not found',
    pageNotFoundMessage: 'This address does not match an available page.',
    backHome: 'Back to home',
    calculatorListLoadTitle: 'Could not load calculators',
    calculatorListLoadMessage:
      'We could not connect to the calculator service. Please try again later.',
    calculatorListLoadingTitle: 'Loading calculators',
    calculatorListLoadingMessage:
      'The calculator list is loading from the backend.',
    apiRequestFailed: 'The backend could not complete the request.',
    apiConnectionFailed:
      'Could not connect to the backend. Please try again later.',
    invalidApiResponse: 'The backend returned an invalid response.',
  },
} as const
