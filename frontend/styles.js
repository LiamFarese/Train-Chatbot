import {StyleSheet} from 'react-native';
import { useTheme } from '@react-navigation/native';

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

        fontSize: 18,
    },

    primary: {

        borderColor: colors.primary,
        backgroundColor: colors.primary,
    },

    header: {

        backgroundColor: colors.card,
        padding: 8,
        alignContent: 'center',
    },

    headerInner: {

        flexDirection: 'row',
    },

    maxWidth: {

        maxWidth: 720,
        alignSelf: 'center',
        width: '100%'
    }
})
