import {StyleSheet} from 'react-native';

export default styles = (colors) => StyleSheet.create({

    container: {

        backgroundColor: colors.card,
        borderColor: colors.border,
        borderRadius: 26,
        borderWidth: 2,

        padding: 8,
        paddingLeft: 16,
        paddingRight: 16,
    },

    text: {

        fontSize: 20,
        color: colors.text,
    },

    title: {

        fontSize: 24,
        fontWeight: 'bold',
    },

    primary: {

        borderColor: colors.primary,
        backgroundColor: colors.primary,
    },

    footer: {

        backgroundColor: colors.backgroundColor,
        padding: 8,
        alignContent: 'center',
    },

    header: {

        backgroundColor: colors.card,
        padding: 8,
        alignContent: 'center',
    },

    headerFooterInner: {

        flexDirection: 'row',
        alignItems: 'center',
    },

    maxWidth: {

        maxWidth: 720,
        alignSelf: 'center',
        width: '100%',
    },

    modal: {

        backgroundColor: colors.card,
        borderRadius: 32,
        shadowColor: colors.border,
        shadowRadius: 32,
    },

    scrollViewContainer: {

        backgroundColor: colors.background,
        borderRadius: 32,
        paddingLeft: 16,
        paddingRight: 16,
        flex: 1,
    },
})
